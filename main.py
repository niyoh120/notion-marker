from dotenv import load_dotenv

load_dotenv()

import notion


def main():
    notion.update_video_database()


if __name__ == "__main__":
    main()
