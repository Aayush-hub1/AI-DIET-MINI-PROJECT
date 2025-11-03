from flask import Flask, render_template, request, jsonify
import random
from mealplans import mealplans

# Create the Flask app
app = Flask(__name__, template_folder='templates')


# Helper function to pick a random meal
def pick_meal(meals):
    return random.choice(meals)


@app.route("/")
def home():
    # Renders your index.html file inside /templates
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_data = data.get("user_data", {})
    more = bool(data.get("more", False))

    # Extract user inputs with safe defaults
    name = user_data.get("name", "User").capitalize()
    gender = user_data.get("gender", "male").lower()
    activity = user_data.get("activity", "medium").lower()

    try:
        weight = float(user_data.get("weight", 0))
    except (TypeError, ValueError):
        weight = 0.0

    try:
        height_cm = float(user_data.get("height", 0))
    except (TypeError, ValueError):
        height_cm = 0.0

    try:
        age = float(user_data.get("age", 25))
    except (TypeError, ValueError):
        age = 25.0

    # Avoid divide by zero
    height_m = height_cm / 100 if height_cm > 0 else 1.0
    bmi = round(weight / (height_m ** 2), 2) if height_m > 0 else 0.0

    # Classify BMI
    if bmi < 18.5:
        category = "low"
        condition = "Underweight"
        advice = "Increase calorie intake with more protein and carbs."
    elif bmi <= 24.9:
        category = "medium"  # ✅ fixed from 'normal' to 'medium'
        condition = "Normal"
        advice = "Maintain your diet and stay consistent."
    else:
        category = "high"
        condition = "Overweight"
        advice = "Reduce sugar and fried foods, increase protein and vegetables."

    # Mifflin-St Jeor Calorie Formula
    if gender == "male":
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) - 161

    # Adjust for activity level
    activity_factor = {"low": 1.2, "medium": 1.5, "high": 1.8}.get(activity, 1.5)
    calories = round(bmr * activity_factor)

    # Choose meals based on BMI category
    try:
        breakfast = pick_meal(mealplans["breakfast"][category])
        lunch = pick_meal(mealplans["lunch"][category])
        dinner = pick_meal(mealplans["dinner"][category])
    except KeyError:
        return jsonify({"error": "Meal data missing. Check mealplans.py"}), 500

    # If user asked for more options, mark meals as alternatives
    if more:
        breakfast = breakfast.copy()
        lunch = lunch.copy()
        dinner = dinner.copy()
        breakfast["name"] += " (Alternative)"
        lunch["name"] += " (Alternative)"
        dinner["name"] += " (Alternative)"

    plan = [breakfast, lunch, dinner]

    # Return data as JSON for the front-end
    return jsonify({
        "name": name,
        "bmi": bmi,
        "condition": condition,
        "advice": advice,
        "calories": calories,
        "plan": plan
    })


if __name__ == "__main__":
    app.run(debug=True)
            
