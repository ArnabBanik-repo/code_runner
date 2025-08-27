import subprocess

from datetime import datetime

from executor.enums.language_enum import Language
from util import create_logger, decode_base64

CODE_FILE_NAME = "Main"
CODE_FILE_PATH = "code"
STAGING_FILE_PATH = "staging"
LOGGER = create_logger("code_runner")


def check_supported_language(language: Language) -> bool:
    LOGGER.info("Checking language support")
    if language not in Language:
        raise ValueError("Unsupported language.")
    return True


def check_compiler(language: Language) -> bool:
    LOGGER.info("Checking compiler availability")
    if language == Language.JAVA:
        try:
            subprocess.run(["javac", "-version"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            raise EnvironmentError("Java compiler not found.")
    return False


def generate_staging_code_filename(user_id: str) -> str:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{CODE_FILE_NAME}_{user_id}_{now}"


def create_code_file(language: Language, code: str, user_id: str) -> str:
    LOGGER.info("Creating code file")
    staging_code_file_name = generate_staging_code_filename(user_id)
    if language == Language.JAVA:
        code_file_name = CODE_FILE_NAME + ".java"
        staging_code_file_name += ".java"
    else:
        code_file_name = CODE_FILE_NAME + ".java"
        staging_code_file_name += ".txt"

    with open(f"{CODE_FILE_PATH}/{code_file_name}", "w") as code_file:
        code_file.write(code)

    with open(f"{STAGING_FILE_PATH}/{staging_code_file_name}", "w") as staging_file:
        staging_file.write(code)

    return code_file_name


def compile_code(language: Language, code_file: str):
    LOGGER.info("Compiling code")
    if language == Language.JAVA:
        try:
            subprocess.run(["javac", code_file], cwd=CODE_FILE_PATH, check=True,
                           capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.stderr)


def execute_code(language: Language, code_file: str) -> str:
    LOGGER.info("Executing code")
    if language == Language.JAVA:
        try:
            result = subprocess.run(["java", CODE_FILE_NAME], cwd=CODE_FILE_PATH, check=True,
                                    capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e.stderr)
    return ""


def run(language: Language, code_b64: bytes, user_id: str) -> int:
    LOGGER.info("Starting code runner")
    try:
        language = Language(language)
        if not user_id:
            raise ValueError("User ID is required.")
        code = decode_base64(code_b64)
        check_supported_language(language)
        check_compiler(language)
        code_file_name = create_code_file(language, code, user_id)
    except Exception as e:
        LOGGER.error(f"Compilation Error:\n{str(e)}")
        return 1

    try:
        compile_code(language, code_file_name)
    except Exception as e:
        LOGGER.error(f"Runtime Error:\n{str(e)}")
        return 1

    try:
        output = execute_code(language, code_file_name)
        LOGGER.info(f"Program output: {output}")
        return 0
    except Exception as e:
        LOGGER.error(e)
        return 1


if __name__ == "__main__":
    from util import encode_base64

    sample_code = """
public class Main {
    private int add(int x, int y) {
        return x + y;
    }
	public static void main(String[] args) {
		int a = 5;
		int b = -9;
		Main main = new Main();
		int res = main.add(a, b);
		System.out.println(res);
	}
}
"""
    run(0,
        encode_base64(sample_code),
        "user123")
