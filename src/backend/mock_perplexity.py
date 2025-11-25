from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/perplexity", methods=["POST", "GET"])
def perplexity_mock():
    # Support GET for quick smoke tests, POST for the expected contract
    if request.method == "GET":
        q = request.args.get("q") or request.args.get("query") or "test"
    else:
        body = request.get_json(silent=True) or {}
        q = body.get("query") or body.get("q") or "test"

    # Return a predictable response shape the app expects
    results = [
        {
            "title": f"Mock event for {q}",
            "snippet": f"This is a mock Perplexity result for query '{q}'.",
            "link": f"https://example.com/events/{q.replace(' ', '-')}",
        }
        for _ in range(3)
    ]

    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=True)
