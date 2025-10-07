#!/usr/bin/env python
import requests
import os
import sys
import argparse
import sqlite3

from fink_mlflow_controller.logger import get_fink_logger


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def main():
    """User management in MLFlow Fink"""
    parser = argparse.ArgumentParser(description=__doc__)

    # Create subparsers for 'create' and 'delete'
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create parser for 'create' command
    create_parser = subparsers.add_parser("create", help="Create a user")
    create_parser.add_argument(
        "-username", type=str, help="The user name", required=True
    )
    create_parser.add_argument(
        "-password",
        type=str,
        help="The password. Must be at least 12 characters",
        required=True,
    )
    create_parser.add_argument(
        "--is_admin",
        action="store_true",
        help="If specified, promote the user as admin.",
    )

    # Create parser for 'delete' command
    delete_parser = subparsers.add_parser("delete", help="Delete a user")
    delete_parser.add_argument(
        "-username", type=str, help="The user name", required=True
    )

    list_parser = subparsers.add_parser("list", help="List users")  # noqa: F841

    args = parser.parse_args(None)

    logger = get_fink_logger("mlflow-users", "INFO")

    if args.command == "create":
        # Create user
        r = requests.post(
            "https://mlflow-dev.fink-broker.org/api/2.0/mlflow/users/create",
            json={"username": args.username, "password": args.password},
            auth=(os.environ["FINK_ADMIN_USERNAME"], os.environ["FINK_ADMIN_PWD"]),
        )

        if r.status_code != 200:
            logger.error(
                "Something went wrong in creating user with username {} and password {}: {}".format(
                    args.username, args.password, r.content
                )
            )
            sys.exit(1)

        logger.info(
            "User {} with password {} created".format(args.username, args.password)
        )

        if args.is_admin:
            r = requests.patch(
                "https://mlflow-dev.fink-broker.org/api/2.0/mlflow/users/update-admin",
                json={"username": args.username, "is_admin": True},
                auth=(os.environ["FINK_ADMIN_USERNAME"], os.environ["FINK_ADMIN_PWD"]),
            )

            if r.status_code != 200:
                logger.error(
                    "Something went wrong in promoting {} as admin: {}".format(
                        args.username, r.content
                    )
                )
                sys.exit(1)

            logger.info(
                "User {} promoted admin successfuly".format(
                    args.username,
                )
            )

    elif args.command == "delete":
        r = requests.delete(
            "https://mlflow-dev.fink-broker.org/api/2.0/mlflow/users/delete",
            json={"username": args.username},
            auth=(os.environ["FINK_ADMIN_USERNAME"], os.environ["FINK_ADMIN_PWD"]),
        )

        if r.status_code != 200:
            logger.error(
                "Something went wrong in deleting user with username {}: {}".format(
                    args.username, r.content
                )
            )
            sys.exit(1)
        logger.info("User {} successfuly deleted".format(args.username))
    elif args.command == "list":
        # Connect to the SQLite database
        conn = sqlite3.connect(
            "/opt/mlflow/basic_auth.db"
        )  # Replace with your database filename
        cursor = conn.cursor()

        # Fetch and display all users from the 'users' table
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()

        print("Users:")
        for user in users:
            if user[3] == 1:
                color = bcolors.WARNING
            else:
                color = bcolors.OKBLUE
            print(
                "userid={}".format(user[0]),
                color + "username={}".format(user[1]) + bcolors.ENDC,
            )

        # Close the connection
        conn.close()


if __name__ == "__main__":
    main()
