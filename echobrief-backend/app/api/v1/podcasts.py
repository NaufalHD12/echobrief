from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_session
from ...models.podcasts import PodcastStatus, PodcastTopic
from ...models.users import PlanType, User
from ...schemas.articles import ArticleResponse
from ...schemas.common import ApiResponse
from ...schemas.podcasts import (
    PodcastCreate,
    PodcastListResponse,
    PodcastQuickCreate,
    PodcastResponse,
    PodcastSegmentResponse,
)
from ...schemas.topics import TopicResponse
from ...services.podcast_service import PodcastService
from ...services.user_service import UserService

router = APIRouter(prefix="/podcasts", tags=["podcasts"])


async def get_podcast_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PodcastService:
    return PodcastService(session)


@router.post(
    "/",
    response_model=ApiResponse[PodcastResponse],
    status_code=201,
    summary="Create podcast request",
    description="Request generation of a new podcast. Uses user's favorite topics if topic_ids not provided.",
)
async def create_podcast(
    service: Annotated[PodcastService, Depends(get_podcast_service)],
    current_user: User = Depends(get_current_user),
    podcast_data: PodcastCreate | None = None,
) -> ApiResponse[PodcastResponse]:
    """
    Create a new podcast request.

    - **topic_ids**: Optional list of topic IDs. If not provided, uses user's favorite topics.
    """
    # Determine topic_ids to use
    if podcast_data and podcast_data.topic_ids:
        topic_ids = podcast_data.topic_ids
    else:
        # Get user's favorite topics
        user_service = UserService(service.session)
        user_topics = await user_service.get_user_topics(current_user.id)

        if not user_topics:
            raise HTTPException(
                status_code=400,
                detail="No topics selected. Please select favorite topics first or provide topic_ids.",
            )

        topic_ids = [topic.id for topic in user_topics if topic.id is not None]

    # Create podcast with determined topic_ids
    podcast_create_data = PodcastCreate(topic_ids=topic_ids)
    podcast = await service.create_podcast_request(
        current_user.id, podcast_create_data, current_user
    )

    response_data = PodcastResponse(
        id=podcast.id,
        user_id=podcast.user_id,
        generated_script=podcast.generated_script,
        audio_url=podcast.audio_url,
        duration_seconds=podcast.duration_seconds,
        status=podcast.status,
        created_at=podcast.created_at,
        topics=[],  # Will be populated from relations
        articles=[],
        segments=[],
    )

    return ApiResponse(
        message="Podcast request created successfully", data=response_data
    )


@router.get(
    "/",
    response_model=ApiResponse[PodcastListResponse],
    summary="Get user podcasts",
    description="Retrieve paginated list of user's podcasts with optional search",
)
async def get_podcasts(
    service: Annotated[PodcastService, Depends(get_podcast_service)],
    search: Annotated[str | None, Query(description="Search in topic names")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[PodcastListResponse]:
    """
    Get paginated list of user's podcasts with optional search.

    - **search**: Optional search term for topic names associated with podcasts (case-insensitive)
    - **page**: Page number (starts from 1)
    - **per_page**: Number of items per page (max 100, default 10)
    """
    skip = (page - 1) * per_page
    podcasts, total = await service.get_user_podcasts(
        current_user.id, skip=skip, limit=per_page, search=search
    )

    podcast_responses = []
    for podcast in podcasts:
        relations = await service.get_podcast_with_relations(podcast.id)
        if relations:
            # Convert model objects to response schemas
            topics_response = [
                TopicResponse(id=topic.id, name=topic.name, slug=topic.slug)
                for topic in relations["topics"]
            ]
            articles_response = [
                ArticleResponse(
                    id=article.id,
                    source_id=article.source_id,
                    topic_id=article.topic_id,
                    title=article.title,
                    summary_text=article.summary_text,
                    url=article.url,
                    published_at=article.published_at,
                    fetched_at=article.fetched_at,
                )
                for article in relations["articles"]
            ]
            segments_response = [
                PodcastSegmentResponse(
                    id=segment.id,
                    podcast_id=segment.podcast_id,
                    title=segment.title,
                    start_second=segment.start_second,
                    end_second=segment.end_second,
                )
                for segment in relations["segments"]
            ]

            podcast_responses.append(
                PodcastResponse(
                    id=podcast.id,
                    user_id=podcast.user_id,
                    generated_script=podcast.generated_script,
                    audio_url=podcast.audio_url,
                    duration_seconds=podcast.duration_seconds,
                    status=podcast.status,
                    created_at=podcast.created_at,
                    topics=topics_response,
                    articles=articles_response,
                    segments=segments_response,
                )
            )

    return ApiResponse(
        message="Podcasts retrieved successfully",
        data=PodcastListResponse(
            items=podcast_responses,
            total=total,
            page=page,
            per_page=per_page,
        ),
    )


@router.get(
    "/{podcast_id}",
    response_model=ApiResponse[PodcastResponse],
    summary="Get podcast by ID",
    description="Retrieve a specific podcast by its ID",
)
async def get_podcast(
    podcast_id: Annotated[UUID, Path(description="Podcast ID")],
    service: Annotated[PodcastService, Depends(get_podcast_service)],
    current_user: User = Depends(get_current_user),
) -> ApiResponse[PodcastResponse]:
    """
    Get podcast by ID.

    - **podcast_id**: Unique identifier of the podcast
    """
    # Check ownership
    podcast = await service.get_podcast_by_id(podcast_id)
    if not podcast or podcast.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Podcast not found")

    relations = await service.get_podcast_with_relations(podcast_id)

    if relations:
        # Convert model objects to response schemas
        topics_response = [
            TopicResponse(id=topic.id, name=topic.name, slug=topic.slug)
            for topic in relations["topics"]
        ]
        articles_response = [
            ArticleResponse(
                id=article.id,
                source_id=article.source_id,
                topic_id=article.topic_id,
                title=article.title,
                summary_text=article.summary_text,
                url=article.url,
                published_at=article.published_at,
                fetched_at=article.fetched_at,
            )
            for article in relations["articles"]
        ]
        segments_response = [
            PodcastSegmentResponse(
                id=segment.id,
                podcast_id=segment.podcast_id,
                title=segment.title,
                start_second=segment.start_second,
                end_second=segment.end_second,
            )
            for segment in relations["segments"]
        ]
    else:
        topics_response = []
        articles_response = []
        segments_response = []

    response_data = PodcastResponse(
        id=podcast.id,
        user_id=podcast.user_id,
        generated_script=podcast.generated_script,
        audio_url=podcast.audio_url,
        duration_seconds=podcast.duration_seconds,
        status=podcast.status,
        created_at=podcast.created_at,
        topics=topics_response,
        articles=articles_response,
        segments=segments_response,
    )

    return ApiResponse(message="Podcast retrieved successfully", data=response_data)


@router.post(
    "/{podcast_id}/generate-script",
    response_model=ApiResponse[dict],
    summary="Generate podcast script",
    description="Generate AI script for the podcast",
)
async def generate_script(
    podcast_id: Annotated[UUID, Path(description="Podcast ID")],
    service: Annotated[PodcastService, Depends(get_podcast_service)],
    current_user: User = Depends(get_current_user),
) -> ApiResponse[dict]:
    """
    Generate podcast script using AI.

    - **podcast_id**: Unique identifier of the podcast
    """
    # Check ownership
    podcast = await service.get_podcast_by_id(podcast_id)
    if not podcast or podcast.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Podcast not found")

    script = await service.generate_podcast_script(podcast_id)

    return ApiResponse(
        message="Podcast script generated successfully", data={"script": script}
    )


@router.post(
    "/{podcast_id}/generate-audio",
    response_model=ApiResponse[dict],
    summary="Generate podcast audio",
    description="Generate audio file for the podcast using TTS",
)
async def generate_audio(
    podcast_id: Annotated[UUID, Path(description="Podcast ID")],
    service: Annotated[PodcastService, Depends(get_podcast_service)],
    current_user: User = Depends(get_current_user),
) -> ApiResponse[dict]:
    """
    Generate podcast audio using TTS.

    - **podcast_id**: Unique identifier of the podcast
    """
    # Check ownership
    podcast = await service.get_podcast_by_id(podcast_id)
    if not podcast or podcast.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Podcast not found")

    audio_result = await service.generate_podcast_audio(podcast_id)

    return ApiResponse(
        message="Podcast audio generated successfully", data=audio_result
    )





@router.post(
    "/quick-generate",
    response_model=ApiResponse[PodcastResponse],
    summary="Quick podcast generation",
    description="Generate podcast quickly using hybrid approach (cached + real-time)",
)
async def quick_generate_podcast(
    request_data: PodcastQuickCreate,
    service: Annotated[PodcastService, Depends(get_podcast_service)],
    current_user: User = Depends(get_current_user),
) -> ApiResponse[PodcastResponse]:
    """
    Quick podcast generation with hybrid approach.

    - **use_cached**: Use cached podcast if available (default: True)
    - **custom_topic_ids**: List of topic IDs (optional, uses favorite topics if not provided)
      Example: [1, 2, 3] or null/empty to use favorite topics
    """
    user_service = UserService(service.session)

    # Determine topic_ids
    if request_data.custom_topic_ids:
        topic_ids = request_data.custom_topic_ids
    else:
        user_topics = await user_service.get_user_topics(current_user.id)
        if not user_topics:
            raise HTTPException(
                status_code=400,
                detail="No favorite topics selected. Please select topics first.",
            )
        topic_ids = [topic.id for topic in user_topics if topic.id is not None]

    # Check cache first if enabled
    if request_data.use_cached:
        # Look for today's podcast with same topics
        today = datetime.now(timezone.utc).date()
        todays_podcasts = await service._get_user_podcasts_today(current_user.id, today)

        for podcast in todays_podcasts:
            # Get podcast topics
            query = select(PodcastTopic.topic_id).where(
                PodcastTopic.podcast_id == podcast.id
            )
            result = await service.session.exec(query)
            podcast_topic_ids = list(result.all())

            # Check if podcast has all requested topics
            if (
                set(topic_ids) == set(podcast_topic_ids)
                and podcast.status == "completed"
            ):
                # Return cached podcast
                relations = await service.get_podcast_with_relations(podcast.id)
                if relations:
                    topics_response = [
                        TopicResponse(id=topic.id, name=topic.name, slug=topic.slug)
                        for topic in relations["topics"]
                    ]
                    articles_response = [
                        ArticleResponse(
                            id=article.id,
                            source_id=article.source_id,
                            topic_id=article.topic_id,
                            title=article.title,
                            summary_text=article.summary_text,
                            url=article.url,
                            published_at=article.published_at,
                            fetched_at=article.fetched_at,
                        )
                        for article in relations["articles"]
                    ]
                    segments_response = [
                        PodcastSegmentResponse(
                            id=segment.id,
                            podcast_id=segment.podcast_id,
                            title=segment.title,
                            start_second=segment.start_second,
                            end_second=segment.end_second,
                        )
                        for segment in relations["segments"]
                    ]

                    response_data = PodcastResponse(
                        id=podcast.id,
                        user_id=podcast.user_id,
                        generated_script=podcast.generated_script,
                        audio_url=podcast.audio_url,
                        duration_seconds=podcast.duration_seconds,
                        status=podcast.status,
                        created_at=podcast.created_at,
                        topics=topics_response,
                        articles=articles_response,
                        segments=segments_response,
                    )

                    return ApiResponse(
                        message="Cached podcast retrieved successfully",
                        data=response_data,
                    )

    # Check plan restrictions for real-time generation
    if current_user.plan_type == PlanType.FREE.value and not request_data.use_cached:
        raise HTTPException(
            status_code=400,
            detail="Free plan can only use cached podcasts. Set use_cached=True or upgrade to paid plan.",
        )

    # Generate new podcast
    podcast_create_data = PodcastCreate(topic_ids=topic_ids)
    podcast = await service.create_podcast_request(
        current_user.id, podcast_create_data, current_user
    )

    # Generate podcast script and audio
    try:
        # Generate script
        script = await service.generate_podcast_script(podcast.id)
        if script:
            podcast.generated_script = script
            podcast.status = PodcastStatus.processing
            await service.session.commit()
            await service.session.refresh(podcast)

        # Generate audio
        audio_result = await service.generate_podcast_audio(podcast.id)
        if audio_result and "audio_url" in audio_result:
            podcast.audio_url = audio_result["audio_url"]
            podcast.duration_seconds = audio_result.get("duration_seconds", 0)
            podcast.status = PodcastStatus.completed
        else:
            podcast.status = PodcastStatus.failed

        await service.session.commit()
        await service.session.refresh(podcast)

    except Exception:
        # Log error but continue to return response
        podcast.status = PodcastStatus.failed
        await service.session.commit()
        await service.session.refresh(podcast)

    # Get relations for response
    relations = await service.get_podcast_with_relations(podcast.id)
    if relations:
        topics_response = [
            TopicResponse(id=topic.id, name=topic.name, slug=topic.slug)
            for topic in relations["topics"]
        ]
        articles_response = [
            ArticleResponse(
                id=article.id,
                source_id=article.source_id,
                topic_id=article.topic_id,
                title=article.title,
                summary_text=article.summary_text,
                url=article.url,
                published_at=article.published_at,
                fetched_at=article.fetched_at,
            )
            for article in relations["articles"]
        ]
        segments_response = [
            PodcastSegmentResponse(
                id=segment.id,
                podcast_id=segment.podcast_id,
                title=segment.title,
                start_second=segment.start_second,
                end_second=segment.end_second,
            )
            for segment in relations["segments"]
        ]
    else:
        topics_response = []
        articles_response = []
        segments_response = []

    # Determine response message based on status
    if podcast.status == "completed":
        message = "Podcast generated successfully"
    elif podcast.status == "processing":
        message = "Podcast script generated, audio generation in progress"
    elif podcast.status == "failed":
        # Check if we have script but no audio
        if podcast.generated_script and not podcast.audio_url:
            message = "Podcast script generated but audio generation failed"
        else:
            message = "Podcast generation failed, please try again"
    else:
        message = "Podcast generation started"

    response_data = PodcastResponse(
        id=podcast.id,
        user_id=podcast.user_id,
        generated_script=podcast.generated_script,
        audio_url=podcast.audio_url,
        duration_seconds=podcast.duration_seconds,
        status=podcast.status,
        created_at=podcast.created_at,
        topics=topics_response,
        articles=articles_response,
        segments=segments_response,
    )

    return ApiResponse(message=message, data=response_data)
