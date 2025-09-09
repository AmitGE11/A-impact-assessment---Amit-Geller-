# Data Directory

This directory contains the requirements data for the Licensure Buddy IL application.

## requirements.sample.json

This file contains sample business licensing requirements in Hebrew. Each requirement includes:

- **id**: Unique identifier
- **title**: Hebrew title of the requirement
- **category**: Category (בטיחות, היגיינה, רישוי כללי)
- **priority**: Priority level (High, Medium, Low)
- **description**: Detailed description in Hebrew
- **conditions**: Matching conditions object with optional fields:
  - `size_any`: Array of business sizes that match
  - `min_seats`: Minimum number of seats required
  - `max_seats`: Maximum number of seats allowed
  - `features_any`: Any of these features must be present
  - `features_all`: All of these features must be present
  - `features_none`: None of these features should be present

## Next Steps

In the next phase, this data will be parsed from the provided PDF/Word documents containing the actual Israeli business licensing requirements.
