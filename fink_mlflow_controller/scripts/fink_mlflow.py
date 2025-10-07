#!/usr/bin/env python
import requests
import os
import sys
import argparse

from fink_mlflow_controller.logger import get_fink_logger

def main():
    """User management in MLFlow Fink"""
    parser = argparse.ArgumentParser(description=__doc__)

    # Create subparsers for 'create' and 'delete'
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Create parser for 'create' command
    create_parser = subparsers.add_parser('create', help='Create a user')
    create_parser.add_argument('-username', type=str, help='The user name', required=True)
    create_parser.add_argument('-password', type=str, help='The password. Must be at least 12 characters', required=True)
    create_parser.add_argument(
        "--is_admin",
        action="store_true",
        help="If specified, promote the user as admin.",
    )

    # Create parser for 'delete' command
    delete_parser = subparsers.add_parser('delete', help='Delete a user')
    delete_parser.add_argument('-username', type=str, help='The user name', required=True)

    list_parser = subparsers.add_parser('list', help='List users')

    args = parser.parse_args(None)

    logger = get_fink_logger("mlflow-users", "INFO")

    if args.command == "create":
        # Create user
        r = requests.post(
            "https://mlflow-dev.fink-broker.org/api/2.0/mlflow/users/create",
            json={"username": args.username, "password": args.password},
            auth=("fink", os.environ["FINK_ADMIN_PWD"])
        )

        if r.status_code != 200:
            logger.error("Something went wrong in creating user with username {} and password {}: {}".format(args.username, args.password, r.content))
            sys.exit(1)

        logger.info("User {} with password {} created".format(args.username, args.password))
        
        if args.is_admin:
            r = requests.patch(
                "https://mlflow-dev.fink-broker.org/api/2.0/mlflow/users/update-admin",
                json={"username": args.username, "is_admin": True},
                auth=("fink", os.environ["FINK_ADMIN_PWD"])
            )

            if r.status_code != 200:
                logger.error("Something went wrong in promoting {} as admin: {}".format(args.username, r.content))
                sys.exit(1)

            logger.info("User {} promoted admin successfuly".format(args.username, args.password))

    elif args.command == "delete":
        r = requests.delete(
            "https://mlflow-dev.fink-broker.org/api/2.0/mlflow/users/delete",
            json={"username": args.username},
            auth=("fink", os.environ["FINK_ADMIN_PWD"])
        )

        if r.status_code != 200:
            logger.error("Something went wrong in deleting user with username {}: {}".format(args.username, r.content))
            sys.exit(1)
        logger.info("User {} successfuly deleted".format(args.username))
    elif args.command == "list":
        # Connect to the SQLite database
        conn = sqlite3.connect('/opt/mlflow/basic_auth.db')  # Replace with your database filename
        cursor = conn.cursor()

        # Fetch and display all users from the 'users' table
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()

        print("Users:")
        for user in users:
            print(user)

        # Close the connection
        conn.close()


if __name__ == "__main__":
    main()

