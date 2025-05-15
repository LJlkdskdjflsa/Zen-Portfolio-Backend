#!/usr/bin/env python3
"""
Script to fetch yield pools from DeFi Llama API and store them in the database and as JSON files.
"""

import os
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db_context
from app.repositories.YieldPoolRepository import YieldPoolRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class YieldPoolFetcher:
    """
    Class for fetching and processing yield pool data from DeFi Llama
    """

    DEFI_LLAMA_API_URL = "https://yields.llama.fi/pools"

    def __init__(self):
        """Initialize the fetcher"""
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "input"
        )
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_yield_pools(
        self,
        chain: Optional[str] = None,
        project: Optional[str] = None,
        min_tvl: Optional[float] = None,
        min_apy: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch yield pools from DeFi Llama API with optional filtering

        Args:
            chain: Filter by blockchain chain
            project: Filter by project name
            min_tvl: Minimum TVL in USD
            min_apy: Minimum APY percentage

        Returns:
            List of yield pool dictionaries
        """
        logger.info(f"Fetching data from {self.DEFI_LLAMA_API_URL}...")

        response = requests.get(self.DEFI_LLAMA_API_URL)
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()
        pools = data.get("data", [])

        logger.info(f"Fetched {len(pools)} pools from DeFi Llama")

        # Apply filters if provided
        if any([chain, project, min_tvl, min_apy]):
            logger.info(
                f"Applying filters: chain={chain}, project={project}, min_tvl={min_tvl}, min_apy={min_apy}"
            )

            filtered_pools = pools

            if chain:
                filtered_pools = [
                    pool
                    for pool in filtered_pools
                    if pool["chain"].lower() == chain.lower()
                ]

            if project:
                filtered_pools = [
                    pool
                    for pool in filtered_pools
                    if project.lower() in pool["project"].lower()
                ]

            if min_tvl is not None:
                filtered_pools = [
                    pool for pool in filtered_pools if pool["tvlUsd"] >= min_tvl
                ]

            if min_apy is not None:
                filtered_pools = [
                    pool for pool in filtered_pools if pool["apy"] >= min_apy
                ]

            logger.info(f"After filtering: {len(filtered_pools)} pools remaining")
            return filtered_pools

        return pools

    def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Save data to a JSON file

        Args:
            data: The data to save
            filename: The filename to save to

        Returns:
            The full path to the saved file
        """
        filepath = os.path.join(self.data_dir, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Data successfully saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {str(e)}")
            raise

    def save_to_database(self, pools: List[Dict[str, Any]], db_session: Session) -> int:
        """
        Save yield pool data to the database

        Args:
            pools: List of yield pool data
            db_session: Database session

        Returns:
            Number of records created
        """
        logger.info(f"Saving {len(pools)} pools to database...")

        try:
            repo = YieldPoolRepository(db_session)
            created_count = repo.create_many(pools)

            logger.info(f"Successfully saved {created_count} pools to database")
            return created_count
        except Exception as e:
            logger.error(f"Error saving pools to database: {str(e)}")
            raise


def main():
    """Main function to fetch and save yield pools"""
    parser = argparse.ArgumentParser(
        description="Fetch yield pools from DeFi Llama API"
    )
    parser.add_argument("--chain", type=str, help="Filter by blockchain chain")
    parser.add_argument("--project", type=str, help="Filter by project name")
    parser.add_argument("--min-tvl", type=float, help="Minimum TVL in USD")
    parser.add_argument("--min-apy", type=float, help="Minimum APY percentage")

    args = parser.parse_args()

    try:
        # Create fetcher
        fetcher = YieldPoolFetcher()

        # Fetch data
        pools = fetcher.fetch_yield_pools(
            chain=args.chain,
            project=args.project,
            min_tvl=args.min_tvl,
            min_apy=args.min_apy,
        )

        # Create filename with filters and timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"defillama-pools-{timestamp}"

        if args.chain:
            filename += f"-{args.chain}"
        if args.project:
            filename += f"-{args.project}"
        if args.min_tvl:
            filename += f"-minTvl{args.min_tvl}"
        if args.min_apy:
            filename += f"-minApy{args.min_apy}"

        filename += ".json"

        # Save to JSON files
        fetcher.save_to_json(pools, filename)
        fetcher.save_to_json(pools, "defillama-pools-latest.json")

        # Save to database
        logger.info("Saving data to database...")
        try:
            with get_db_context() as db:
                created_count = fetcher.save_to_database(pools, db)
                logger.info(f"Successfully saved {created_count} records to database")
        except Exception as db_error:
            logger.error(f"Error saving to database: {str(db_error)}")
            logger.info("Continuing with JSON output only...")

        logger.info("Process completed successfully")

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise


if __name__ == "__main__":
    main()
