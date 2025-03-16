import os
from flask import Flask, jsonify, request
from app import json_parser, topics_matcher  # Ensure correct import path

app = Flask(__name__)

# Homepage route to confirm app is running
@app.route("/")
def home():
    return "Hello from Bids2Match! Your service is running."

# Existing API route
@app.route('/match_topics', methods=['POST'])
def topic_matching():
    # Attempt to get JSON from the request without forcing an error.
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Bad Request", "message": "No JSON input provided"}), 400

    # Try to parse the input.
    try:
        input_parsed_model = json_parser.JsonParser(data)
    except Exception as e:
        return jsonify({
            "error": "Bad Request",
            "message": f"Invalid input: {str(e)}"
        }), 400

    # Try to run the matching algorithm.
    try:
        assigned_topics_model = topics_matcher.TopicsMatcher(
            input_parsed_model.student_ids,
            input_parsed_model.topic_ids,
            input_parsed_model.student_priorities_dict,
            input_parsed_model.topic_priorities_dict,
            input_parsed_model.max_accepted_proposals
        )
        result = assigned_topics_model.get_student_topic_matches()
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": f"An error occurred during matching: {str(e)}"
        }), 500

    return jsonify(result), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)
