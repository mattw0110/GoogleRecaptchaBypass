#!/usr/bin/env python3
"""
Proxy Refresh Script for GoogleRecaptchaBypass

This script fetches fresh proxies from multiple sources, tests them,
and updates the working_proxies.json file with verified working proxies.
"""

import sys
import os
import argparse
import time
from datetime import datetime
from typing import List, Dict

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from proxy_manager import ProxyManager, get_proxy_stats, get_proxy_status
except ImportError:
    print("❌ Error: Could not import proxy_manager. Please run from project directory.")
    sys.exit(1)


def print_banner():
    """Print script banner."""
    print("=" * 60)
    print("🔄 Google reCAPTCHA Bypass - Proxy Refresh Tool")
    print("=" * 60)
    print()


def print_stats(manager: ProxyManager, title: str = "Current Stats"):
    """Print current proxy statistics."""
    stats = get_proxy_stats()
    status = get_proxy_status()

    print(f"📊 {title}:")
    print(f"   Total proxies: {stats['total_proxies']}")
    print(f"   Success rate: {stats['avg_success_rate']:.1f}%")
    print(f"   Total successes: {stats['total_success']}")
    print(f"   Total failures: {stats['total_failures']}")
    print(f"   Last refresh: {stats['last_refresh']}")
    print(f"   Status: {status}")
    print()


def fetch_new_proxies(manager: ProxyManager, test_count: int = 50) -> List[Dict]:
    """Fetch and test new proxies."""
    print("🌐 Fetching proxy lists from sources...")

    # Fetch raw proxy list
    raw_proxies = manager.fetch_proxy_list()
    if not raw_proxies:
        print("❌ No proxies found from any source")
        return []

    print(f"📥 Found {len(raw_proxies)} proxy candidates")

    # Test a subset of proxies
    test_proxies = raw_proxies[:test_count] if len(
        raw_proxies) > test_count else raw_proxies
    print(f"🧪 Testing {len(test_proxies)} proxies...")

    start_time = time.time()
    working_proxies = manager.test_proxies_batch(test_proxies, max_workers=20)
    test_time = time.time() - start_time

    success_rate = (len(working_proxies) / len(test_proxies)) * \
        100 if test_proxies else 0

    print(
        f"✅ Found {len(working_proxies)} working proxies ({success_rate:.1f}% success rate)")
    print(f"⏱️  Testing completed in {test_time:.1f} seconds")
    print()

    return working_proxies


def clean_old_proxies(manager: ProxyManager, max_failures: int = 3) -> int:
    """Remove proxies with too many failures."""
    print(f"🧹 Cleaning proxies with more than {max_failures} failures...")

    initial_count = len(manager.working_proxies)
    manager.working_proxies = [
        p for p in manager.working_proxies
        if p.get('fail_count', 0) <= max_failures
    ]
    removed_count = initial_count - len(manager.working_proxies)

    if removed_count > 0:
        print(f"🗑️  Removed {removed_count} failed proxies")
        manager.save_working_proxies()
    else:
        print("✅ No proxies needed cleaning")

    print()
    return removed_count


def merge_proxies(manager: ProxyManager, new_proxies: List[Dict], avoid_duplicates: bool = True) -> int:
    """Merge new proxies with existing ones."""
    if not new_proxies:
        return 0

    print("🔀 Merging new proxies with existing ones...")

    initial_count = len(manager.working_proxies)
    existing_proxies = {p['proxy']
                        for p in manager.working_proxies} if avoid_duplicates else set()

    added_count = 0
    for proxy_data in new_proxies:
        if not avoid_duplicates or proxy_data['proxy'] not in existing_proxies:
            manager.working_proxies.append(proxy_data)
            added_count += 1

    print(f"➕ Added {added_count} new working proxies")
    if avoid_duplicates and len(new_proxies) - added_count > 0:
        print(
            f"⚠️  Skipped {len(new_proxies) - added_count} duplicate proxies")

    manager.save_working_proxies()
    print()
    return added_count


def test_existing_proxies(manager: ProxyManager, sample_size: int = 10) -> None:
    """Test a sample of existing proxies to verify they still work."""
    if not manager.working_proxies:
        print("ℹ️  No existing proxies to test")
        return

    import random

    test_count = min(sample_size, len(manager.working_proxies))
    test_proxies = random.sample(manager.working_proxies, test_count)

    print(f"🔍 Testing {test_count} existing proxies...")

    working_count = 0
    for proxy_data in test_proxies:
        if manager.test_proxy(proxy_data['proxy']):
            working_count += 1

    success_rate = (working_count / test_count) * 100 if test_count else 0
    print(
        f"📈 Existing proxy health: {working_count}/{test_count} working ({success_rate:.1f}%)")
    print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Refresh proxy list for reCAPTCHA bypass")
    parser.add_argument('--force', '-f', action='store_true',
                        help='Force refresh even if we have enough proxies')
    parser.add_argument('--test-count', '-t', type=int, default=50,
                        help='Number of new proxies to test (default: 50)')
    parser.add_argument('--clean', '-c', action='store_true',
                        help='Clean failed proxies before fetching new ones')
    parser.add_argument('--test-existing', '-e', action='store_true',
                        help='Test a sample of existing proxies')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='Show current proxy statistics and exit')
    parser.add_argument('--max-failures', type=int, default=3,
                        help='Maximum failures before removing proxy (default: 3)')

    args = parser.parse_args()

    print_banner()

    # Initialize proxy manager
    try:
        manager = ProxyManager()
    except Exception as e:
        print(f"❌ Failed to initialize proxy manager: {e}")
        sys.exit(1)

    # Show current stats
    print_stats(manager, "Initial Stats")

    # If only stats requested, exit
    if args.stats:
        return

    # Test existing proxies if requested
    if args.test_existing:
        test_existing_proxies(manager)

    # Clean old proxies if requested
    if args.clean:
        clean_old_proxies(manager, args.max_failures)

    # Check if refresh is needed
    if not args.force and len(manager.working_proxies) >= manager.min_proxies:
        print(
            f"ℹ️  Have {len(manager.working_proxies)} working proxies (minimum: {manager.min_proxies})")
        print("   Use --force to refresh anyway")
        return

    # Fetch new proxies
    new_proxies = fetch_new_proxies(manager, args.test_count)

    # Merge new proxies
    if new_proxies:
        added_count = merge_proxies(manager, new_proxies)

        if added_count > 0:
            print_stats(manager, "Updated Stats")
            print("✅ Proxy refresh completed successfully!")
        else:
            print("ℹ️  No new proxies were added (all were duplicates)")
    else:
        print("❌ No working proxies found. Check your internet connection.")

    print()
    print("🚀 Ready for reCAPTCHA solving!")
    print("   Start service: ./start_fake_2captcha_with_chrome.sh")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
