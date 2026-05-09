# DonationAssist Implementation Plan

## Introduction

This implementation plan explains how the DonationAssist group project will be completed, installed, released, and maintained. DonationAssist is a Django-based donation assistance web application designed for smaller non-profit organizations that need a simple way to manage requested inventory items and help donors choose the most useful items to donate. The plan uses information from the project source code, the M02 Project Plan, and the DevOps Tool Chain Document. It includes the purpose of the project, the implementation strategy, the pros and cons of common implementation methods, requirement-to-implementation details, installation instructions, and a final summary. Team members should use this document as a guide for development, testing, deployment preparation, and final submission.

The application scope is housed inside the Django framework. Non-profit staff manage inventory items through the administrative interface, while donors use two client-facing pages: a prioritized donation list and a donation cart. The donation list is based on inventory thresholds so that items with higher need appear first, while low-urgency items can be hidden from the donor view. The implementation plan also reflects the team's DevOps approach, including Discord for communication, Jira for Agile/Scrum planning, GitHub for version control, and a dependency file for consistent local setup.

## Implementation Methods Pro and Cons

Real-world IT projects can be implemented in several ways depending on risk tolerance, budget, schedule, user readiness, and system complexity. The three most common implementation strategies are phased implementation, parallel implementation, and big bang implementation.

| Method | Description | Pros | Cons | Best Use Cases |
| --- | --- | --- | --- | --- |
| Phased Implementation | The system is released in stages, such as by feature, user group, department, or module. | Reduces risk by limiting each release to a smaller part of the system. Makes testing, training, and feedback easier because users adopt the application gradually. Lets the team fix issues before later phases depend on them. | Takes longer than a full immediate release. Requires planning so each phase is useful on its own. May require temporary workarounds while not all features are complete. | Larger or more complex systems, multi-team projects, and applications where stability is more important than speed. |
| Parallel Implementation | The old system and new system run at the same time for a set period. | Provides the safest transition because the old system remains available. Allows users to compare results between systems and verify that data is accurate. Reduces the chance of operational failure during the switch. | Costs more because two systems and two workflows must be supported. Can create extra work for users and administrators. Requires clear rules for which system is the final source of truth. | Financial systems, mission-critical systems, and organizations where downtime or incorrect data would be unacceptable. |
| Big Bang Implementation | The entire organization switches to the new system at one time. | Fastest path to full adoption. Lower short-term cost because the team avoids supporting two live systems. Useful when the system is small or the old process cannot continue. | Highest implementation risk because a major problem affects the whole system. Requires strong testing, training, backup plans, and user readiness before release. | Small organizations, simple systems, deadline-driven transitions, or systems with limited users and limited operational risk. |

### Chosen Strategy: Phased Implementation

The selected strategy for DonationAssist is phased implementation supported by Agile/Scrum task management. This is the best fit because the application is built from clear modules that can be completed and validated separately: inventory data modeling, priority threshold logic, Amazon product data lookup, the donor item list, session-based cart behavior, cart summary, administrator workflow, testing, and release preparation. A phased strategy also matches the group project organization because team members can focus on different work areas while still integrating the system one stable piece at a time.

This method was chosen over parallel implementation because DonationAssist does not currently replace a large live legacy system. Running an old donation system and the new Django system at the same time would create extra work without giving the project much additional value. It was also chosen over big bang implementation because the project contains several connected parts, including database migrations, external API integration, session state, templates, administrative data entry, and planned testing. Delivering everything at once would increase the chance that one incomplete feature could affect the entire application. Phased implementation lets the team verify each major feature before moving to the next phase.

The recommended rollout phases are:

1. Retain the current source code and create a stable development environment.
2. Finalize the inventory model, database migrations, and Django Admin workflow.
3. Implement and test inventory priority calculations based on maximum quantities and thresholds.
4. Implement the ecommerce/Amazon product information integration in the service layer.
5. Build the customer-facing donation list and cart interface.
6. Test full functionality, including item display, add-to-cart, remove-from-cart, totals, and admin updates.
7. Prepare release documentation, known limitations, and deployment configuration.

The project plan also identifies major risks that support this phased approach. Team illness, availability conflicts, local software failures, and hardware issues can slow progress, so the team plans to share responsibilities when needed and set up environments early. Project complexity is a higher risk because ecommerce API work can take more time than expected. The team reduces that risk by focusing on one ecommerce source, keeping the Django application scope manageable, and testing features iteratively instead of waiting until the final deadline.

## Details

### Requirement 1: Serve smaller non-profit organizations and donors

The main project requirement is to create a donation assistance application that can be used by small non-profit organizations. This requirement is implemented by structuring the system around two user groups: staff members and donors. Staff members use Django Admin to maintain requested inventory items, while donors use the public donation list and cart pages. This matches the project plan's goal of making item donation easier for both the organization and the donor. The current Django project is named `DonationAssist`, and the core app is named `inventory`, which keeps the project focused on donation inventory management.

### Requirement 2: Store donation inventory information

DonationAssist must store the item information needed by the organization and donors. This requirement is implemented in `inventory/models.py` through the `Item` model. The model stores Amazon product URLs, Amazon image URLs, wishlist URLs, item name, category, current quantity, maximum quantity, priority level, estimated price, and percentage thresholds. This gives the application one central database record for each requested donation item. SQLite is configured in `DonationAssist/settings.py`, which supports local development and class demonstration without requiring a separate database server.

### Requirement 3: Provide an administrative interface for non-profit staff

The project plan states that inventory items will be added by the non-profit through the admin interface. This requirement is implemented in `inventory/admin.py`, where the `Item` model is registered with Django Admin. The admin list view displays item names, product images, priority levels, quantities, and estimated prices. The custom `fetch_amazon_data` action saves selected records again, which triggers the model's Amazon data refresh behavior. This gives staff members a practical way to add, review, and update donation items without directly editing the database.

### Requirement 4: Calculate item urgency from inventory thresholds

The application must identify which requested items are most urgent so donors can focus on the highest need. This requirement is implemented by the `calculate_urgency()` method in `inventory/models.py`. The method compares current quantity against maximum quantity, then assigns a priority level using configurable percentage thresholds from `lvl_1` through `lvl_5`. The `save()` method calls `calculate_urgency()` automatically, so priority is refreshed whenever an item record is saved. This directly supports the project plan requirement that donation list prioritization be based on maximum quantity and threshold percentages.

### Requirement 5: Hide or deprioritize low-urgency items

The project plan states that items with the lowest urgency should be hidden from the client-facing list. This requirement is implemented in `InventoryLogic.get_prioritized_items()` in `inventory/services.py`. The query filters for items with `priority_level__gt=1`, which prevents the lowest-priority items from appearing in the donor list. It also orders the remaining items by descending priority level. This keeps the donor interface focused on items that the organization actually needs and avoids encouraging donations for inventory that is already close to full.

### Requirement 6: Show donors a prioritized donation list

Donors need a clear list of requested items so they can decide what to give. This requirement is implemented through `InventoryLogic.get_items_with_name_price_image()` in `inventory/services.py`, the `item_list()` view in `inventory/views.py`, and the `inventory/templates/inventory/item_list.html` template. The view retrieves prioritized item data from the service layer and renders it in a customer-facing table. The template displays the item name, quantity, image, priority, estimated price, quantity input, and add-to-cart button. This corresponds to the customer website and donation list described in the project plan and DevOps document.

### Requirement 7: Enrich item data through an ecommerce API

The work breakdown and risk plan identify ecommerce API research and implementation as a major part of the project. The current application implements this requirement with the `AmazonApi` class in `inventory/services.py` and the overridden `save()` method of the `Item` model in `inventory/models.py`. When an item is saved, the application extracts the ASIN from the Amazon product URL and calls SerpAPI to request product information. If product data is available, the application fills missing item names, images, and estimated prices. This keeps the integration focused on one ecommerce source, which matches the team's risk plan for controlling complexity.

### Requirement 8: Let donors add selected quantities to a donation cart

DonationAssist must let donors select items and quantities before reviewing the donation. This requirement is implemented by the add-to-cart form in `inventory/templates/inventory/item_list.html`, the `add_to_cart()` view in `inventory/views.py`, and the `DonationCart.add_item_to_session_cart()` method in `inventory/services.py`. The view reads the posted quantity, converts invalid input to a safe default value, and stores the selection in the Django session. Using session storage keeps the cart tied to the current donor visit without requiring account creation or a permanent cart table.

### Requirement 9: Display cart details and estimated totals

Donors need to review their selected items before completing or reporting a donation. This requirement is implemented by the `view_cart()` view in `inventory/views.py` and the `inventory/templates/inventory/donation_cart.html` template. The view reads cart data from the session, retrieves matching `Item` records from the database, calculates each line total from estimated price and quantity, and calculates the grand total. The template displays the item name, image, price, quantity, line total, and overall total so the donor can clearly understand the estimated value of the donation.

### Requirement 10: Allow donors to remove items from the cart

The cart must be editable so donors can correct mistakes or change their donation decision. This requirement is implemented by the remove form in `inventory/templates/inventory/donation_cart.html`, the `remove_from_cart()` view in `inventory/views.py`, and the `DonationCart.delete_item_from_session_cart()` method in `inventory/services.py`. The service method removes the item from the session dictionary, marks the session as modified, and returns a user message. The view sends that message through Django's message framework, and `inventory/templates/inventory/base.html` displays the alert to the donor.

### Requirement 11: Use Django routing, templates, static files, and sessions

The project must operate as a web application with navigable pages and persistent session state. This requirement is implemented through `DonationAssist/urls.py`, `inventory/urls.py`, the templates in `inventory/templates/inventory/`, the stylesheet in `inventory/static/inventory/css/inventory.css`, and Django's default session middleware in `DonationAssist/settings.py`. The root URL displays the donation list, `/cart/` displays the cart, `/add/<item_id>/` adds items, and `/cart/remove/<item_id>/` removes them. Bootstrap and the custom stylesheet provide the basic user interface styling.

### Requirement 12: Support team collaboration and DevOps practices

The DevOps Tool Chain Document requires the team to use Discord for communication, Jira for Agile/Scrum planning, and GitHub for version control, branching, and code review. This requirement is supported by the repository structure, the GitHub-based workflow, the `.github` project notes, and `requirements.txt` for dependency consistency. Jira should be used to track feature work, defects, dependencies, due dates, and future iterations. Discord should be used for team communication, screen sharing, and file sharing that does not belong in the repository. GitHub branch protection and review practices should be used before merging stable code into the main branch.

### Requirement 13: Build, test, release, and secure the application

The DevOps document identifies build, test, release, package, deploy, operate, and secure activities. The current project supports local builds through a Python virtual environment, `requirements.txt`, Django migrations, and `manage.py`. Testing should include Django system checks, unit tests for models and services, and end-to-end checks for item selection and cart operations. Release preparation should include tagging a stable version in GitHub and preparing release notes that list features, known limitations, and fixes. Environment-specific values such as API keys and secrets should be stored in environment variables instead of hard-coded in source files.

## Installation Instructions

These instructions describe how to install and run DonationAssist locally. A standard laptop or desktop computer with a keyboard, mouse, monitor, terminal, browser, Python, and Git is sufficient for development and review.

1. Open a terminal and move into the project folder.

   ```bash
   cd "/Users/cadeau/SDEV265-Sys Software Analysis/SDEV220-Group-Project"
   ```

2. Create and activate a Python virtual environment if one is not already available.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows, activate the environment with:

   ```bash
   venv\Scripts\activate
   ```

3. Install the project dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root if Amazon product lookup will be used. Add a SerpAPI key in this format:

   ```text
   SERPAPI_KEY=your_serpapi_key_here
   ```

   The application can still be reviewed locally without calling the Amazon lookup feature, but saving new Amazon-linked items may require a valid key.

5. Apply database migrations.

   ```bash
   python manage.py migrate
   ```

6. Optional: create an administrator account for Django Admin.

   ```bash
   python manage.py createsuperuser
   ```

7. Start the Django development server.

   ```bash
   python manage.py runserver
   ```

8. Open the donor item list in a browser:

   ```text
   http://127.0.0.1:8000/
   ```

9. Open the administrator site, if an admin account was created:

   ```text
   http://127.0.0.1:8000/admin/
   ```

10. Verify the project setup with Django's system check and test command.

    ```bash
    python manage.py check
    python manage.py test
    ```

11. For team development, create a feature branch in GitHub, link the work to a Jira task when applicable, and open a pull request before merging into the stable branch. Release notes should be prepared when the team tags a stable version.

## Summary

DonationAssist is being implemented as a phased Django project because its major features can be developed, tested, and reviewed in logical stages. The application supports the project goal of helping smaller non-profit organizations manage donation needs while giving donors a simple customer-facing donation list and cart. It stores donation inventory records, calculates urgency from inventory thresholds, hides low-urgency items, displays prioritized requested items, enriches product data through Amazon and SerpAPI, manages a session-based donation cart, calculates donation totals, supports cart item removal, and provides administrator management through Django Admin.

This implementation plan also connects the software to the team's project-management and DevOps decisions. Discord supports communication, Jira supports Agile/Scrum planning and defect tracking, and GitHub supports version control, branch protection, code review, dependency tracking, release tagging, and release notes. The main implementation risks are schedule pressure, ecommerce API complexity, team availability, and environment setup issues. The phased implementation strategy reduces those risks by allowing the team to complete, test, and stabilize each feature before moving to the next phase.
