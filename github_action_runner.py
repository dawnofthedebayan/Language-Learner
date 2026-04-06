import os
import sys


def setup_env() -> None:
    required = [
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "NEWS_API_KEY",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"[Runner] WARNING: Missing env vars: {', '.join(missing)}")


def write_github_summary(content: str) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("## 🇩🇪 German Lesson of the Day\n\n")
            f.write("```\n")
            f.write(content)
            f.write("\n```\n")


def run() -> None:
    setup_env()
    import main as lesson_main
    result = lesson_main.main()
    if result:
        write_github_summary(result)


if __name__ == "__main__":
    run()
