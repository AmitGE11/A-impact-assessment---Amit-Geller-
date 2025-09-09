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

## requirements.json

This file is produced by `process_pdf.py` from the source PDF document. It contains the same schema as `requirements.sample.json`:

- **id**: Unique identifier (format: req-XXX)
- **category**: Category (בטיחות, היגיינה, רישוי כללי)
- **title**: Hebrew title of the requirement
- **description**: Detailed description in Hebrew
- **priority**: Priority level (High, Medium, Low)
- **conditions**: Matching conditions object with optional fields:
  - `size_any`: Array of business sizes that match
  - `min_seats`: Minimum number of seats required
  - `max_seats`: Maximum number of seats allowed
  - `features_any`: Any of these features must be present
  - `features_all`: All of these features must be present
  - `features_none`: None of these features should be present

The parser uses a simple heuristic split and keyword-based category guess; manual tuning is expected later.

## Next Steps

The data processing pipeline is now complete. Future enhancements may include:
- Improved text parsing algorithms
- More sophisticated category detection
- Enhanced condition extraction from requirement text
