from flask import Flask, render_template, request, redirect, url_for, flash
from main import run_scraper, start_driver, manual_login
import pandas as pd
import os
from flask import send_file

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/", methods=["GET", "POST"])
def index():
    cleaned_data = None
    cleaned_path = "Data/Scraping Result/Cleaned_Linkedin_SCU_Alumni_2025.csv"

    if request.method == "POST":
        location_class = request.form.get("location_class").strip()
        section_class = request.form.get("section_class").strip()
        max_profiles = int(request.form.get("max_profiles", 10))
        save_mode = request.form.get("save_mode", "append")
        overwrite = save_mode == "overwrite"

        # Upload name list
        uploaded_file = request.files.get("name_csv")
        if uploaded_file and uploaded_file.filename.endswith(".csv"):
            os.makedirs("Data/Person Locations", exist_ok=True)
            uploaded_file.save("Data/Person Locations/Indonesia_names.csv")
            flash("✅ Name list uploaded successfully.")

        # Upload existing data if appending
        existing_scraped_file = request.files.get("existing_csv")
        if existing_scraped_file and existing_scraped_file.filename.endswith(".csv") and not overwrite:
            os.makedirs("Data", exist_ok=True)
            existing_scraped_file.save("Data/Linkedin_SCU_Alumni_2025.csv")
            flash("✅ Existing scraped data uploaded for appending.")

        # ✅ This check should be here
        if not location_class or not section_class:
            flash("Please provide both class names.")
            return redirect(url_for("index"))

        run_scraper(location_class, section_class, max_profiles, overwrite)

        if os.path.exists(cleaned_path):
            df = pd.read_csv(cleaned_path)
            cleaned_data = df.head(10).to_dict(orient="records")
            flash("✅ Scraping and cleaning completed.")

    return render_template("index.html", cleaned_data=cleaned_data)

@app.route("/login")
def login():
    start_driver()
    manual_login()
    return "🔑 Browser opened. Please log into LinkedIn manually, then return and submit the form."

@app.route("/download")
def download_cleaned():
    path = "Data/Scraping Result/Cleaned_Linkedin_SCU_Alumni_2025.csv"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    flash("❌ Cleaned file not found.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
