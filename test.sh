#!/bin/bash

PYTHON_VERSION="3.11"

isMacOS() {
    [[ "$OSTYPE" == "darwin"* ]]
}

isLinux() {
    [[ "$OSTYPE" == "linux-gnu"* ]]
}

install_pyenv_via_homebrew() {
    echo "Detected macOS. Installing pyenv using Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Homebrew is not installed. Please install Homebrew, or update this script to add your preferred package installer."
        exit 1
    fi
    brew install pyenv
    configure_pyenv_for_shell
}

install_pyenv_via_apt() {
    echo "Detected Linux. Installing pyenv using apt..."
    if ! command -v apt &> /dev/null; then
        echo "apt is not available. Please install it, or update this script to add your preferred package installer."
        exit 1
    fi

    # Install dependencies for pyenv on Linux
    sudo apt update
    sudo apt install -y make build-essential libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
        libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
        liblzma-dev python3-openssl git

    # Clone pyenv from GitHub and set it up
    curl https://pyenv.run | bash

    configure_pyenv_for_shell
}

configure_pyenv_for_shell() {
    shell_config=""

    if [[ "$SHELL" == */bash ]]; then
        if [ -f "$HOME/.bashrc" ]; then
            shell_config="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            shell_config="$HOME/.bash_profile"
        fi
    elif [[ "$SHELL" == */zsh ]]; then
        shell_config="$HOME/.zshrc"
    else
        echo "Unknown shell. Please manually add pyenv initialization to your shell's startup script."
        return 1
    fi

    if [[ -n "$shell_config" ]]; then
        echo "Adding pyenv initialization to $shell_config"
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> "$shell_config"
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> "$shell_config"
        echo 'eval "$(pyenv init --path)"' >> "$shell_config"
        echo 'eval "$(pyenv init -)"' >> "$shell_config"
    fi
}

install_pyenv_if_not_already_installed() {
    if ! command -v pyenv &> /dev/null; then
        echo "pyenv is not installed. Installing pyenv..."

        if isMacOS; then
            install_pyenv_via_homebrew
        elif isLinux; then
            install_pyenv_via_apt
        else
            echo "Apologies, we didn't expect anyone to be using anything other than MacOS or Linux. Have you considered changing operating systems? :D (Please install pyenv manually.)"
            exit 1
        fi
        echo "pyenv installation completed."
    else
        echo "pyenv is already installed."
    fi
}

initialise_pyenv() {
    if command -v pyenv &> /dev/null; then
        eval "$(pyenv init --path)"
        eval "$(pyenv init -)"
    else
        echo "pyenv installation failed or not properly configured. Please check the installation."
        exit 1
    fi
}

install_python_if_not_already_installed() {
    if ! pyenv versions | grep "$PYTHON_VERSION" &> /dev/null; then
        echo "Python $PYTHON_VERSION is not installed. Attempting to install using pyenv..."

        pyenv install "$PYTHON_VERSION"
    else
        echo "Python $PYTHON_VERSION is already installed via pyenv."
    fi

    pyenv global "$PYTHON_VERSION"
}

create_virtual_env() {
    python3 -m venv .venv
    source .venv/bin/activate
}

install_pytest_if_not_already_installed() {
    if ! python3 -m pytest --version &> /dev/null; then
        echo "pytest is not installed. Installing pytest..."
        pip install pytest
    else
        echo "pytest is already installed."
    fi
}

run_all_test_suites() {
    # Find all directories under src/functions/ that contain a 'tests' subdirectory
    find src/functions/ -type d -name 'tests' | while read test_dir; do
        # Derive the function directory from the test directory path
        function_dir=$(dirname "$test_dir")

        echo "Processing function directory: $function_dir"

        # Check if requirements.txt exists in the function directory and install dependencies
        if [ -f "$function_dir/requirements.txt" ]; then
            echo "Installing requirements for $function_dir"
            pip install -r "$function_dir/requirements.txt"
        else
            echo "No requirements.txt found in $function_dir"
        fi

        # Run tests located in the current tests directory
        echo "Running tests in $test_dir"
        pytest "$test_dir" || { echo "Tests failed in $test_dir"; exit 1; }
    done
}

# Actually run the things
install_pyenv_if_not_already_installed
initialise_pyenv
install_python_if_not_already_installed
create_virtual_env
install_pytest_if_not_already_installed
run_all_test_suites
