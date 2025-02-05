# plan
building_plan_prompt = """
You are a professional city land-use planner. Your task is to assist in making land-use plans for city regions of various sizes. Each region is represented as a grid where each cell corresponds to 0.5 meters in the real world.
The positions for ground, buildings, traffic roads, rails, waters, vegetation, and footpaths have been pre-planned.

You will be provided with:
(1) A 2D semantic layout image where:
    - Black represents ground
    - White represents traffic roads
    - Yellow represents footpaths
    - Blue represents water
    - Magenta represents rails
    - Green represents vegetation
    - Cyan represents buildings
    The target building is purple and its neighbors are marked with red numbers in the image for easy reference.

(2) The location and dimensions of the building to be planned
(3) Information about surrounding buildings and infrastructures
(4) General land-use planning principles requirements
(5) User requirements

Each building location is represented as a bounding box (x, y, w, h) where (x,y) is the top left corner of the building, w is the width and h is the height of the bounding box.
For each surrounding building, information is provided in the following format: (x, y, w, h) | description | primary function | secondary function | architectural style | building size

During planning, you should consider both the semantic layout and these general requirements:
1.Zoning Compliance: Ensure building functions align with designated zoning laws and the surrounding infrastructure visible in the layout
2.Function Compatibility: (1) Residential buildings should not be adjacent to industrial buildings or rails. (2) Nearby buildings tend to have similar primary functions but can vary to meet specific needs.
3.Distance from Traffic Roads: Residential buildings should be at least 5 meters away from traffic roads (white areas in the layout).
4.Green Space Integration: Consider proximity to vegetation (green areas) when planning residential or recreational buildings.
5.Accessibility: Ensure buildings are accessible via footpaths (yellow areas) and consider proximity to public transport (rails - magenta areas).
6.Water Proximity: For buildings near water bodies (blue areas), consider appropriate functions like recreational or hospitality.
7.Architectural Harmony: Buildings should generally complement the architectural style of the surrounding area.
8.User requirements (if any): Your final plan should satisfy the user requirements, including planning correct amount of user required building types, and satisfying additional requirements. Generally, you should prioritize planning user-required buildings if requirements are unmet. However, if you believe a location is better suited for another type of building, that's acceptable, as long as there are enough unplanned buildings remaining to meet the user's requirements.

Instructions: Now I have a building at location {input_location}, with maxmimum length {length} meters, maximum width {width} meters, and {distance_to_roads} meters away from traffic roads.
Its surrounding buildings are: {neighbor_information}, and they are marked with red numbers in the image for easy reference.
Additional user requirements: (1) {requirements_string} (2) {additional_requirements}.

Your task: Please follow the general requirements and user requirements, based on the given information, provide your plan for the building in the following format: description|primary function|secondary function|architectural style|building size| reason
Description: A concise description of the proposed building.
Primary Function: The main purpose of the building (e.g., residential, commercial).
Secondary Function: Any secondary purpose (e.g., retail, office).
Architectural Style: The architectural style (e.g., modern, traditional).
Building Size: The size category (e.g., low-rise, mid-rise, high-rise).
Reason: A brief explanation summarizing your choices based on the general requirements.

Output Instructions:
(1) Be concise and provide only the required information.
(2) Do not include any extra content at the beginning or the end.
(3) Summarize your reasoning in the "reason" field.
(4) If you plan to allocate a user required building at this location, include the name of the require building in your plan. 

Example: Planning the land use for a building at location (312, 442, 41, 30), width 20.5 meters, length 15 meters.

Its surrounding buildings are:
Neighbour 1: (330, 404, 38, 33) | commercial | warehouse | modern | low-rise
Neighbour 2: (308, 490, 28, 27) | commercial | grocery store| modern | low-rise
Neighbour 3: (274, 479, 22, 23) | commercial | fruit store | modern | low-rise
Neighbour 4: (378, 463, 31, 27) | commercial | nail store | modern | low-rise
Neighbour 5: (256, 419, 27, 26) | residential | townhouse | modern | low-rise

Distance from traffic roads: 9.5 meters

Sample output: A two-floor hair salon | commercial | service | modern | low-rise | Complements nearby commercial services and fulfills community needs

"""

# refine
building_refine_prompt = """
Context: 
You are a professional city land-use planner assisting in refining a land-use plan for a 2D city region of various sizes, where each cell represents 0.5 meters in the real world. The positions for ground, buildings, traffic roads, rails, waters, vegetation, and footpaths have been pre-planned.
Each building location is represented as a bounding box (x, y, w, h), where: (x, y) is the top-left corner of the building, w is the width, h is the height.
You have previously helped plan all buildings. However, initial plans might have been made without complete information about surrounding buildings, leading to possible inaccuracies. 

Your task: 
(1) After assessing the new information about surrounding buildings and infrastructures, decide whether to keep your previous plan or make changes based on the updated context.
(2) If your previous plan (including the "reason" field) remains suitable and requires no changes, output the word "keep" and do not provide any new plan or reasoning, even if your understanding or justification has changed.
(3) If you decide to modify your plan (any changes in description, primary function, secondary function, architectural style, building size, or reason), provide a new plan in the specified format, including the "reason" field.
(4) Note: The "reason" field is part of the plan. Only if there are changes in any of the fields (description, primary function, secondary function, architectural style, building size, or reason), should you consider it a modification and provide a new plan.

Information Provided:
(1) Building to be refined: Location: {input_location}, Maximum Length: {length} meters, Maximum Width: {width} meters, Distance from Traffic Roads: {distance_to_roads} meters. 
(2) Surrounding Buildings: {neighbor_information} 
(3) User requirements: {requirements_string} {additional_requirements}.
(4) Your previous plan: {self_information}.

General Requirements: 
(1) Zoning Compliance: Ensure building functions align with designated zoning laws (e.g., residential, commercial, industrial).
(2) Function Compatibility: Residential buildings should not be adjacent to industrial buildings. Buildings should complement the functions of the surrounding area, and nearby buildings tend to have similar functions but can vary to meet specific needs.
(3) Proximity to Traffic Roads: Residential buildings should be at least 10 meters away from traffic roads.
(4) Architectural Harmony: Buildings should complement the architectural style of the surrounding area.
(5) Accessibility and Sustainability: Incorporate accessibility features and consider sustainable design principles.
(6) Safety Regulations: Comply with local building codes, fire safety, and health regulations.
(7) User requirements (if any): Your final plan should satisfy the user requirements, including planning correct amount of user required building types, and satisfying additional requirements.
(8) Generally, you should prioritize planning user-required buildings if requirements are unmet. However, if you believe a location is better suited for another type of building, that's acceptable, as long as there are enough unplanned buildings remaining to meet the user's requirements.
(9) Ensure your plan aligns with the general and additional requirements.


Output Instructions:
(1) If your previous plan is acceptable based on the updated information and requirements, you should output the word "keep" and do not provide any new plan or reasoning.
(2) If you decide to modify your plan, provide a new plan in the following format: description | primary function | secondary function | architectural style | building size | reason, and summarize your reasoning in the "reason" field. 
(3) Be concise and provide only the required information. Do not include any extra content at the beginning or the end.

Description: A concise description of the proposed building.
Primary Function: The main purpose of the building (e.g., residential, commercial).
Secondary Function: Any secondary purpose (e.g., retail, office).
Architectural Style: The architectural style (e.g., modern, traditional).
Building Size: The size category (e.g., low-rise, mid-rise, high-rise).
Reason: A brief explanation summarizing your new reasoning.

Example 1:
Building to be refined: Location: (312, 442, 41, 30) Distance from Traffic Roads: 9.5 meters
Surrounding Buildings:
Neighbour 1: (330, 404, 38, 33) | warehouse | commercial | storage | modern | low-rise
Neighbour 2: (308, 490, 28, 27) | grocery store | commercial | retail | modern | low-rise
Neighbour 3: (274, 479, 22, 23) | fruit store | commercial | retail | modern | low-rise
Neighbour 4: (378, 463, 31, 27) | nail salon | commercial | service | modern | low-rise
Neighbour 5: (256, 419, 27, 26) | townhouse | residential | housing | modern | low-rise

Your Previous Plan: A two-floor hair salon | commercial | service | modern | low-rise | Complements nearby commercial services and fulfills community needs.
Example Output:  "keep"

Example 2: 
Building to be refined: Location: (312, 442, 41, 30) Distance from Traffic Roads: 9.5 meters
Surrounding Buildings:
Neighbor 1: (330, 404, 38, 33) | warehouse | commercial | storage | modern | low-rise
Neighbor 2: (308, 490, 28, 27) | grocery store | commercial | retail | modern | low-rise
Neighbor 3: (274, 479, 22, 23) | fruit store | commercial | retail | modern | low-rise
Neighbor 4: (378, 463, 31, 27) | nail salon | commercial | service | modern | low-rise
Neighbor 5: (256, 419, 27, 26) | townhouse | residential | housing | modern | low-rise
Your Previous Plan: A two-floor hair salon | commercial | service | modern | low-rise | Complements nearby commercial services and fulfills community needs.
Example Output: A two-floor coffee shop | commercial | café | modern | low-rise | Enhances community space and aligns with nearby retail.
"""

# parse user requirement
parse_user_requirement_prompt = """

You are an expert urban planner assistant. Your task is to parse user requirements for urban planning projects into quantifiable and actionable specifications.

Your Tasks:

Quantified Requirements:
- Extract all specific requirements that mention quantities or counts of items (e.g., "I want 2 hospitals", "There should be 3 parks").
- For requirements that are not quantified but can be reasonably quantified (e.g., "I need a hospital in this region", "There should be some stores in this region"), use the given information (such as the total number of buildings, locations, and standard urban planning practices) to decide the exact number of required buildings in the region.
- List each item with its count.

Additional Requirements:
- Extract any general, qualitative requirements that are not easily quantifiable (e.g., "I want a vibrant city center", "Buildings should have modern architecture").
- List each as a separate string in a list.

Instructions:

- Use all provided information, including the number of buildings, locations of buildings, and all user requirements.
- Ensure that the parsing is reasonable and that the quantified requirements are decided thoughtfully. You don't need to specify types for all buildings, only some specific buildings that should be included in the plan, the number of buildings in quantified_requirements should be less than the total number of buildings.
- Provide the output in valid JSON format with two keys: "quantified_requirements" and "additional_requirements".

Example:

User Requirements:
"The region should include community service centers and feature traditional style buildings. There are 40 buildings in total."

Output:
 ```json
{{
    "quantified_requirements": [
        {{"item": "community service centers", "count": 2}},
        {{"item": "residential buildings", "count": 12}},
        {{"item": "commercial buildings", "count": 6}}
    ],
    "additional_requirements": [
        "Buildings should feature traditional style architecture"
    ]
}}

Now, please process the following user input: {user_input}
"""

# evaluate plan
evaluation_prompt = """
I am a city planner, and I have created a building plan for a given layout, which includes the buildings' locations, dimensions, descriptions, primary and secondary functions, architectural styles, building sizes, and more.

Layout Representation:
The layout is a 2D grid image where each cell represents 0.5 meters in the real world. The colors represent the following features:

Black: Ground
White: Traffic roads
Yellow: Footpaths
Blue: Water
Magenta: Rails
Green: Vegetation
Cyan: Buildings

Building Plan Structure

The plan is structured as a Python dictionary, where each building contains the following information:
Building ID
Location: Coordinates of the building's location in the grid.
Dimensions: The building's size in the layout.
Primary Function: The main use of the building (e.g., mixed-use, residential).
Secondary Function: Additional function the building serves (e.g., event space, office).
Architectural Style: The design style of the building (e.g., modern, traditional).
Building Size: The scale of the building (e.g., mid-rise, high-rise).
Number of Floors
Reason: Justification for the building's placement and design.
Distance to Roads: Distance of the building from the nearest road (in meters).


For example:
"1": {
    "location": [0, 78, 14, 34],
    "x": 17.0,
    "y": 7.0,
    "neighbors": [0, 8, 9, 14, 13],
    "description": "A modern eco-friendly community hub",
    "primary_function": "mixed-use",
    "secondary_function": "event space",
    "scale": "mid-rise",
    "style": "modern",
    "num_floor": 0,
    "reason": "Aligns with nearby eco-friendly buildings, meets community needs, and promotes sustainability.",
    "distance_to_roads": [5.0]
}

Evaluation Criteria:
For each building in the plan, answer the following questions. 
If the layout does not contain rails, vegetation, or water, skip the related questions. 
The answers should be output as a list of strings in the following format: ["yes", "no", "uncertain", ...], with each answer corresponding to the respective question.

Questions:

(1) Does the planning model assign building functions that comply with designated zoning laws?
(2) Are the proposed building functions compatible with the surrounding infrastructure visible in the layout?
(3) For buildings near water bodies (blue areas), does the model assign appropriate functions?
(4) Does the model avoid placing residential buildings adjacent to industrial buildings or rails?
(5) Do nearby buildings tend to have similar primary functions?
(6) Does the plan consider functional diversity to meet specific needs while maintaining compatibility?
(7) Are residential buildings placed at least 5 meters away from traffic roads (white areas)?
(8) Does the model consider proximity to vegetation when planning residential or recreational buildings?
(9) Do all buildings have adequate pedestrian access?
(10) Does the model consider proximity to public transport options like rails (magenta areas)?

Your task: 
Now, please evaluate the following building plan: {plan} for the given layout.

Output instructions:
(1) Output your evaluation in the following format: ["yes", "no", "uncertain", ...]
(2) Do not include any extra content at the beginning or the end.

"""