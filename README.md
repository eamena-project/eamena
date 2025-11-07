**Version:** 5  
**Framework:** [Arches Project](https://github.com/archesproject/arches)  

## Overview

EAMENA ("Endangered Archaeology in the Middle East and North Africa") is a project dedicated to the documentation and assessment of archaeological sites across the MENA region. This repository is an Arches-based implementation for managing EAMENA's spatial, descriptive, and heritage data.

Arches is an open-source platform designed for cultural heritage data management. EAMENA leverages its graph database and semantic capabilities to organize and share site data, threats, activities, and historical information.

The EAMENA database is a customised Arches 7.6 instance, which may be installed from this repository.

## Resources

- Main project repository: [eamena-project/eamena](https://github.com/eamena-project/eamena)
- Documentation:  
  - See the [EAMENA Arches Database README](https://github.com/eamena-project/eamena-arches-dev/blob/main/dbs/database.eamena/README.md) for more information on deployment and database structure.
- Arches documentation:  
  - [Arches Documentation](https://arches.readthedocs.io/en/7.6/)

## Getting Started

### Prerequisites

- Python (recommended version per Arches documentation)
- PostgreSQL
- Elasticsearch
- Node.js & npm (for frontend assets)
- Celery and a suitable message queue, such as RabbitMQ
- Familiarity with [Arches](https://github.com/archesproject/arches#installation)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/eamena-project/eamena.git
   cd eamena
   ```
2. **Install dependencies:**  
   Install Python dependencies. It is recommended to do this within a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure database and environment:**  
   See [this guide](https://github.com/eamena-project/eamena-arches-dev/blob/main/dbs/database.eamena/README.md) for EAMENA-specific setup. The Arches package containing all the EAMENA customisations may be installed from the `./pkg` directory.

## Support

If you need more detailed developer or deployment instructions, please see the [database README](https://github.com/eamena-project/eamena-arches-dev/blob/main/dbs/database.eamena/README.md).

