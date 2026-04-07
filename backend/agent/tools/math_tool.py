def calculate_tdee(data: dict) -> float:
    """
    Calculate TDEE (Total Daily Energy Expenditure) based on Mifflin-St Jeor equation.
    
    Args:
        data (dict): Dictionary containing the following keys:
            - gender (str): 'male' or 'female'
            - weight (float): Weight in kg
            - height (float): Height in cm
            - age (int): Age in years
            - activity (float): Activity multiplier (e.g., 1.2 for sedentary, 1.55 for moderate)
            
    Returns:
        float: Calculated TDEE
    """
    gender = data.get("gender", "male").lower()
    weight = float(data.get("weight", 0))
    height = float(data.get("height", 0))
    age = int(data.get("age", 0))
    activity = float(data.get("activity", 1.2))

    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * activity
    return tdee
