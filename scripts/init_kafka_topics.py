#!/usr/bin/env python3
"""
Initialize Kafka topics from configuration file.
"""

import subprocess
import sys
from pathlib import Path

import yaml


def load_topics_config(
    config_path: str = "shared/config/kafka_topics.yml",
) -> list[dict]:
    """Load topics configuration from YAML file."""
    config_file = Path(config_path)

    if not config_file.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    return config.get("topics", [])


def get_kafka_container_id() -> str:
    """Get Kafka container ID."""
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", "name=kafka"],
        capture_output=True,
        text=True,
    )

    container_id = result.stdout.strip()
    if not container_id:
        print("❌ Kafka container not found. Is infrastructure running?")
        print("Run: make infrastructure")
        sys.exit(1)

    return container_id


def create_topic(
    container_id: str,
    name: str,
    partitions: int,
    replication_factor: int,
) -> bool:
    """Create a Kafka topic."""
    cmd = [
        "docker",
        "exec",
        container_id,
        "kafka-topics",
        "--bootstrap-server",
        "localhost:9092",
        "--create",
        "--if-not-exists",
        "--topic",
        name,
        "--partitions",
        str(partitions),
        "--replication-factor",
        str(replication_factor),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return True
    else:
        print(f"   ⚠️  Warning: {result.stderr.strip()}")
        return False


def main():
    """Main function."""
    print("📋 Loading Kafka topics configuration...")
    topics = load_topics_config()

    print(f"✅ Found {len(topics)} topics to create\n")

    print("🔍 Finding Kafka container...")
    container_id = get_kafka_container_id()
    print(f"✅ Kafka container: {container_id}\n")

    print("🚀 Creating topics...\n")

    created = 0
    skipped = 0

    for topic in topics:
        name = topic["name"]
        description = topic.get("description", "")
        partitions = topic.get("partitions", 3)
        replication_factor = topic.get("replication_factor", 1)

        print(f"📌 {name}")
        if description:
            print(f"   {description}")

        if create_topic(container_id, name, partitions, replication_factor):
            print(f"   ✅ Created (partitions: {partitions})")
            created += 1
        else:
            print(f"   ⏭️  Already exists")
            skipped += 1

        print()

    print("=" * 50)
    print(f"✅ Topics created: {created}")
    print(f"⏭️  Topics skipped: {skipped}")
    print(f"📊 Total topics: {len(topics)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
