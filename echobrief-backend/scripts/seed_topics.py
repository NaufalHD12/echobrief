#!/usr/bin/env python3
"""
Seeding script untuk topik-topik beragam di EchoBrief Backend.

Script ini mengisi database dengan topik-topik spesifik yang beragam
untuk keperluan pengembangan dan testing.

Cara menjalankan:
    uv run python scripts/seed_topics.py
    atau
    python -m scripts.seed_topics (dari root directory)
"""

import asyncio
import sys
from pathlib import Path

# Tambahkan path root project ke sys.path
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.insert(0, str(root_dir))

from sqlmodel import select  # noqa: E402
from slugify import slugify  # noqa: E402

from app.core.database import async_session  # noqa: E402
from app.models.topics import Topic  # noqa: E402


# Daftar topik spesifik beragam untuk agregasi berita
DIVERSE_TOPICS = [
    # --- Entertainment ---
    "Entertainment",
    "Celebrities",
    "Movies",
    "TV",
    "Music",
    "Theatre",
    "Gaming",
    "Arts & Design",
    "Books",

    # --- Sports ---
    "Sports",
    "Football",
    "Soccer",
    "Cycling",
    "Motor Sports",
    "Formula 1",
    "MotoGP",
    "Tennis",
    "Combat Sports",
    "UFC",
    "Boxing",
    "Basketball",
    "Baseball",
    "American Football",
    "Sports betting",
    "Water Sports",
    "Cricket",
    "Golf",
    "Athletics",
    "Hockey",

    # --- Technology ---
    "Technology",
    "Mobile",
    "Gadgets",
    "Internet",
    "Virtual Reality",
    "Artificial Intelligence",
    "Cybersecurity",
    "Computing",
    "Robotics",
    "Space",

    # --- Business ---
    "Business",
    "Economy",
    "Markets",
    "Jobs",
    "Personal Finance",
    "Entrepreneurship",
    "Startups",
    "Real Estate",
    "Crypto",

    # --- Science ---
    "Science",
    "Environment",
    "Climate Change",
    "Physics",
    "Biology",
    "Archaeology",
    "Astronomy",
    "Paleontology",

    # --- Health ---
    "Health",
    "Medicine",
    "Healthcare",
    "Mental Health",
    "Nutrition",
    "Fitness",
    "Public Health",

    # --- Lifestyle & General ---
    "Lifestyle",
    "Travel",
    "Food & Drink",
    "Fashion",
    "Beauty",
    "Home & Garden",
    "Automotive",
    "Education",
    "Relationships",
    "Parenting"
]


async def seed_topics() -> None:
    """Seed database dengan topik-topik beragam."""
    print("🚀 Memulai seeding topik...")
    
    async with async_session() as session:
        # Hitung topik yang sudah ada
        existing_topics_query = select(Topic)
        existing_result = await session.exec(existing_topics_query)
        existing_topics = existing_result.all()
        
        if existing_topics:
            print(f"⚠️  Database sudah memiliki {len(existing_topics)} topik.")
            response = input("Apakah Anda ingin menambahkan topik baru? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ Seeding dibatalkan.")
                return
        
        added_count = 0
        skipped_count = 0
        
        for topic_name in DIVERSE_TOPICS:
            # Generate slug dari nama
            slug = slugify(topic_name)
            
            # Cek apakah topik dengan slug yang sama sudah ada
            existing_query = select(Topic).where(Topic.slug == slug)
            existing_result = await session.exec(existing_query)
            existing_topic = existing_result.first()
            
            if existing_topic:
                print(f"⏭️  Topik '{topic_name}' sudah ada (slug: {slug})")
                skipped_count += 1
                continue
            
            # Buat topik baru
            topic = Topic(name=topic_name, slug=slug)
            session.add(topic)
            added_count += 1
            
            print(f"✅ Menambahkan: {topic_name} -> {slug}")
        
        try:
            await session.commit()
            print("\n🎉 Seeding selesai!")
            print(f"   Topik ditambahkan: {added_count}")
            print(f"   Topik dilewati: {skipped_count}")
            print(f"   Total topik dalam daftar: {len(DIVERSE_TOPICS)}")
            
            # Tampilkan statistik
            if added_count > 0:
                final_query = select(Topic)
                final_result = await session.exec(final_query)
                all_topics = final_result.all()
                print(f"   Total topik di database: {len(all_topics)}")
                
        except Exception as e:
            await session.rollback()
            print(f"❌ Error saat commit: {e}")
            raise


async def list_topics() -> None:
    """Menampilkan daftar topik yang ada di database."""
    print("📋 Daftar topik di database:")
    
    async with async_session() as session:
        query = select(Topic).order_by(Topic.name)
        result = await session.exec(query)
        topics = result.all()
        
        if not topics:
            print("   (Database kosong)")
            return
        
        for i, topic in enumerate(topics, 1):
            print(f"   {i:3d}. {topic.name} ({topic.slug})")


async def clear_topics() -> None:
    """Hapus semua topik dari database (hati-hati!)."""
    print("⚠️  PERINGATAN: Ini akan menghapus SEMUA topik dari database!")
    confirmation = input("Ketik 'HAPUS' untuk konfirmasi: ").strip()
    
    if confirmation != "HAPUS":
        print("❌ Penghapusan dibatalkan.")
        return
    
    async with async_session() as session:
        query = select(Topic)
        result = await session.exec(query)
        topics = result.all()
        
        for topic in topics:
            await session.delete(topic)
        
        await session.commit()
        print(f"🗑️  {len(topics)} topik telah dihapus.")


async def main() -> None:
    """Fungsi utama."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seeding script untuk topik EchoBrief")
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="Tampilkan daftar topik yang ada"
    )
    parser.add_argument(
        "--clear", 
        action="store_true", 
        help="Hapus semua topik (hati-hati!)"
    )
    parser.add_argument(
        "--seed", 
        action="store_true", 
        default=True,
        help="Jalankan seeding (default)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.clear:
            await clear_topics()
        elif args.list:
            await list_topics()
        else:
            await seed_topics()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
