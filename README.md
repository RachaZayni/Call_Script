# Call_Script# AI Call Interface for Salesforce

This project integrates an AI call interface with Salesforce, allowing for real-time lead management, sentiment analysis, and event scheduling. It provides a seamless communication experience through voice and text, leveraging the power of GPT-4 for personalized customer interactions.

## Features

* Real-time lead information retrieval from Salesforce
* Sentiment analysis for adaptive responses
* AI-powered conversation management
* Event scheduling based on customer interactions
* Voice and text input modes

## Project Structure

* **accessDatabase.py**: Handles Salesforce API authentication and database access.
* **fillDatabase.py**: Populates Salesforce with fake lead data for testing.
* **main\_code.py**: Main application file, includes the AI agent, call interface, and event scheduling.

## Prerequisites

* Python 3.9+
* Required libraries:

  * `requests`
  * `simple_salesforce`
  * `pydantic`
  * `pydantic_ai`
  * `datetime`
  * `Faker`
  * `transformers`
  * `speech_recognition`
  * `pyttsx3`
  * `customtkinter`

## Setup

1. Clone the repository.
2. Install the required packages:

   ```bash
   pip install requests simple-salesforce pydantic pydantic-ai Faker transformers speechrecognition pyttsx3 customtkinter
   ```
3. Add your Salesforce credentials in **consumer\_details.py**:

   ```python
   CONSUMER_KEY='YOUR_CONSUMER_KEY'
   CONSUMER_SECRET='YOUR_CONSUMER_SECRET'
   USERNAME='YOUR_SALESFORCE_USERNAME'
   PASSWORD='YOUR_SALESFORCE_PASSWORD'
   ```
4. Set your OpenAI API key:

   ```bash
   export OPENAI_API_KEY='sk-your-openai-key'
   ```

## Running the Project

1. Populate Salesforce with test data:

   ```bash
   python fillDatabase.py
   ```
2. Run the main call interface:

   ```bash
   python main_code.py
   ```

## Usage

* **AccessDB**: Retrieves lead information based on phone number.
* **create\_event**: Schedules events in Salesforce.
* **is\_datetime\_occupied**: Checks if a specific date and time are available.

## Customization

* Modify the `positive_prompt`, `negative_prompt`, and `neutral_prompt` in **main\_code.py** to fine-tune agent responses.
* Use different voice or message settings by updating the `UserContext` class.

## Known Issues

* Long response times for speech-to-text conversions.
* Potential authentication timeouts if the access token expires.

## Contributing

Feel free to submit issues or pull requests for improvements.

## License

This project is licensed under the MIT License.

## Contact

For any questions or support, contact **[rachazayni1262@agentforce.com](mailto:rachazayni1262@agentforce.com)**.
