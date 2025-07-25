#!/usr/bin/env python3
"""
Proxy Manager for Anti-Detection
Fetches and rotates proxies from TheSpeedX's proxy list
"""

import requests
import random
import time
import threading
import json
import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProxyManager:
    """Manages proxy rotation for anti-detection."""

    def __init__(self):
        self.proxy_list_urls = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt"
        ]
        self.proxies: List[str] = []
        self.working_proxies: List[Dict] = []
        self.last_fetch: Optional[datetime] = None
        self.fetch_interval = timedelta(hours=1)  # Refresh every hour
        self.lock = threading.Lock()
        self.test_timeout = 10
        self.proxy_file = "working_proxies.json"
        self.max_failures = 3
        self.min_proxies = 5  # Minimum proxies before we need to refresh

        # Load existing working proxies
        self.load_working_proxies()

    def load_working_proxies(self) -> None:
        """Load working proxies from persistent storage."""
        try:
            if os.path.exists(self.proxy_file):
                with open(self.proxy_file, 'r') as f:
                    data = json.load(f)
                    self.working_proxies = data.get('proxies', [])
                    last_refresh = data.get('last_refresh')
                    if last_refresh:
                        self.last_fetch = datetime.fromisoformat(last_refresh)
                    logger.info(
                        f"Loaded {len(self.working_proxies)} working proxies from storage")
            else:
                logger.info(
                    "No existing proxy file found, will fetch fresh proxies")
        except Exception as e:
            logger.error(f"Failed to load working proxies: {e}")
            self.working_proxies = []

    def save_working_proxies(self) -> None:
        """Save working proxies to persistent storage."""
        try:
            data = {
                'proxies': self.working_proxies,
                'last_refresh': self.last_fetch.isoformat() if self.last_fetch else None
            }
            with open(self.proxy_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(
                f"Saved {len(self.working_proxies)} working proxies to storage")
        except Exception as e:
            logger.error(f"Failed to save working proxies: {e}")

    def fetch_proxy_list(self) -> List[str]:
        """Fetch fresh proxy list from multiple sources."""
        all_proxies = set()  # Use set to avoid duplicates

        for url in self.proxy_list_urls:
            try:
                source_name = url.split(
                    '/')[-2] if 'github.com' in url else url.split('/')[-3]
                logger.info(f"Fetching proxy list from {source_name}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Parse proxy list (one proxy per line)
                proxy_list = [proxy.strip()
                              for proxy in response.text.split('\n') if proxy.strip()]
                all_proxies.update(proxy_list)
                logger.info(
                    f"Fetched {len(proxy_list)} proxies from {source_name}")

            except Exception as e:
                logger.error(f"Failed to fetch proxy list from {url}: {e}")
                continue

        # Convert set back to list
        final_proxy_list = list(all_proxies)
        logger.info(
            f"Total unique proxies from all sources: {len(final_proxy_list)}")
        return final_proxy_list

    def test_proxy(self, proxy: str) -> bool:
        """Test if a proxy is working."""
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }

            # Test with a simple request
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=self.test_timeout
            )

            if response.status_code == 200:
                logger.debug(f"Proxy {proxy} is working")
                return True
            else:
                logger.debug(
                    f"Proxy {proxy} failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.debug(f"Proxy {proxy} failed: {e}")
            return False

    def test_proxies_batch(self, proxies: List[str], max_workers: int = 10) -> List[Dict]:
        """Test a batch of proxies and return working ones."""
        working_proxies = []

        def test_single_proxy(proxy):
            if self.test_proxy(proxy):
                working_proxies.append({
                    'proxy': proxy,
                    'last_used': None,
                    'success_count': 0,
                    'fail_count': 0
                })

        # Test proxies in parallel (limited concurrency)
        threads = []
        for i in range(0, len(proxies), max_workers):
            batch = proxies[i:i + max_workers]
            for proxy in batch:
                thread = threading.Thread(
                    target=test_single_proxy, args=(proxy,))
                thread.start()
                threads.append(thread)

            # Wait for batch to complete
            for thread in threads:
                thread.join()
            threads.clear()

        logger.info(
            f"Found {len(working_proxies)} working proxies out of {len(proxies)} tested")
        return working_proxies

    def refresh_proxies(self, force: bool = False) -> None:
        """Refresh the proxy list."""
        with self.lock:
            # Check if we need to refresh
            if not force and self.last_fetch and \
               datetime.now() - self.last_fetch < self.fetch_interval:
                return

            # Only refresh if we have too few working proxies
            if not force and len(self.working_proxies) >= self.min_proxies:
                logger.info(
                    f"Have {len(self.working_proxies)} working proxies, no refresh needed")
                return

            logger.info("Refreshing proxy list...")

            # Fetch new proxy list
            new_proxies = self.fetch_proxy_list()
            if not new_proxies:
                logger.warning("No proxies fetched, keeping existing list")
                return

            # Test a subset of proxies (to avoid too many requests)
            test_count = min(50, len(new_proxies))
            test_proxies = random.sample(new_proxies, test_count)

            # Test proxies
            new_working = self.test_proxies_batch(test_proxies)

            # Merge with existing working proxies (avoid duplicates)
            existing_proxies = {p['proxy'] for p in self.working_proxies}
            for proxy_data in new_working:
                if proxy_data['proxy'] not in existing_proxies:
                    self.working_proxies.append(proxy_data)

            self.last_fetch = datetime.now()

            # Save to persistent storage
            self.save_working_proxies()

            logger.info(
                f"Proxy refresh complete. {len(self.working_proxies)} working proxies available")

    def get_proxy(self) -> Optional[str]:
        """Get a working proxy for use."""
        with self.lock:
            # Refresh if we have no proxies or too few
            if len(self.working_proxies) < self.min_proxies:
                self.refresh_proxies(force=True)

            if not self.working_proxies:
                logger.warning("No working proxies available after refresh")
                return None

            # Select proxy with least recent use
            available_proxies = [
                p for p in self.working_proxies
                if p['last_used'] is None or
                datetime.now() - p['last_used'] > timedelta(minutes=5)
            ]

            if not available_proxies:
                # If all proxies were recently used, use the least recently used
                available_proxies = sorted(
                    self.working_proxies,
                    key=lambda x: x['last_used'] or datetime.min
                )

            # Select random proxy from available ones
            selected = random.choice(available_proxies)
            selected['last_used'] = datetime.now()

            logger.debug(f"Selected proxy: {selected['proxy']}")
            return selected['proxy']

    def mark_proxy_success(self, proxy: str) -> None:
        """Mark a proxy as successful."""
        with self.lock:
            for p in self.working_proxies:
                if p['proxy'] == proxy:
                    p['success_count'] += 1
                    # Save changes periodically (every 10 successes)
                    if p['success_count'] % 10 == 0:
                        self.save_working_proxies()
                    break

    def mark_proxy_failure(self, proxy: str) -> None:
        """Mark a proxy as failed."""
        with self.lock:
            for i, p in enumerate(self.working_proxies):
                if p['proxy'] == proxy:
                    p['fail_count'] += 1
                    # Remove proxy if it fails too often
                    if p['fail_count'] >= self.max_failures:
                        removed_proxy = self.working_proxies.pop(i)
                        logger.info(
                            f"Removed failing proxy: {proxy} (failures: {removed_proxy['fail_count']})")
                        # Save changes to persistent storage
                        self.save_working_proxies()

                        # If we're running low on proxies, trigger a refresh
                        if len(self.working_proxies) < self.min_proxies:
                            logger.info(
                                f"Running low on proxies ({len(self.working_proxies)}), will refresh on next request")
                    break

    def get_proxy_stats(self) -> Dict:
        """Get proxy statistics."""
        with self.lock:
            total_proxies = len(self.working_proxies)
            if total_proxies == 0:
                return {
                    'total_proxies': 0,
                    'avg_success_rate': 0,
                    'last_refresh': self.last_fetch
                }

            total_success = sum(p['success_count']
                                for p in self.working_proxies)
            total_failures = sum(p['fail_count'] for p in self.working_proxies)
            total_attempts = total_success + total_failures

            avg_success_rate = (
                total_success / total_attempts * 100) if total_attempts > 0 else 0

            return {
                'total_proxies': total_proxies,
                'total_success': total_success,
                'total_failures': total_failures,
                'avg_success_rate': round(avg_success_rate, 2),
                'last_refresh': self.last_fetch
            }

    def get_proxy_dict(self, proxy: str) -> Dict[str, str]:
        """Convert proxy string to requests proxy dictionary."""
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }


# Global proxy manager instance
proxy_manager = ProxyManager()


def get_proxy() -> Optional[str]:
    """Get a working proxy."""
    return proxy_manager.get_proxy()


def get_proxy_dict(proxy: str) -> Dict[str, str]:
    """Get proxy dictionary for requests."""
    return proxy_manager.get_proxy_dict(proxy)


def mark_proxy_success(proxy: str) -> None:
    """Mark proxy as successful."""
    proxy_manager.mark_proxy_success(proxy)


def mark_proxy_failure(proxy: str) -> None:
    """Mark proxy as failed."""
    proxy_manager.mark_proxy_failure(proxy)


def get_proxy_stats() -> Dict:
    """Get proxy statistics."""
    return proxy_manager.get_proxy_stats()


def refresh_proxies() -> None:
    """Force refresh proxy list."""
    proxy_manager.refresh_proxies(force=True)


def get_proxy_status() -> Dict:
    """Get detailed proxy status."""
    return {
        'working_proxies': len(proxy_manager.working_proxies),
        'min_proxies': proxy_manager.min_proxies,
        'max_failures': proxy_manager.max_failures,
        'last_refresh': proxy_manager.last_fetch.isoformat() if proxy_manager.last_fetch else None,
        'needs_refresh': len(proxy_manager.working_proxies) < proxy_manager.min_proxies
    }
