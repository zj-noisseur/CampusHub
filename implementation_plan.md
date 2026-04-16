# Implementation Plan

This document outlines the steps required to implement the requested features and improvements for the CampusHub project.

---

## 1. Add Institution-Based Filtering to Club Admin Page

### **Objective**
Enhance the Django admin interface for the `Club` model by adding a filter to allow administrators to easily filter clubs and societies based on their associated institution.

### **Steps**


#### **Phase 2: Customize the Admin Interface**
1. **Modify the Club Admin Class**
   - Open the `admin.py` file for the `core` app.
   - Locate the `ClubAdmin` class (or create one if it doesn’t exist).

2. **Add the Institution Filter**
   - Use Django’s `list_filter` attribute to add the `institution` field as a filter.
   - Example:
     ```python
     class ClubAdmin(admin.ModelAdmin):
         list_display = ('name', 'institution', 'created_at')  # Example fields
         list_filter = ('institution',)  # Add institution filter
     ```

3. **Register the ClubAdmin Class**
   - Ensure the `ClubAdmin` class is registered with the `Club` model:
     ```python
     from django.contrib import admin
     from .models import Club

     admin.site.register(Club, ClubAdmin)
     ```

#### **Phase 3: Test the Feature**
1. **Verify the Admin Page**
   - Log in to the Django admin interface.
   - Navigate to the `Club` model page.
   - Confirm that a filter for `institution` appears in the right-hand sidebar.

2. **Test Filtering**
   - Use the filter to display clubs associated with specific institutions.
   - Verify that the results are accurate.

---

## 2. Refactor Scraper Logic and Integrate with Dashboard

### **Objective**
Refactor the current proof-of-concept scraper in `apify.py` into a robust, reusable, and dashboard-accessible Django view. The scraper will fetch Instagram data for clubs, store it in the database, and manage temporary JSON files.

### **Steps**

#### **Phase 1: Refactor Scraper Logic**
1. **Extract IG Handle from Database**
   - Query the database for the club's Instagram handle (`ig_handle`) based on the club's identifier.
   - Validate that the handle exists before proceeding.

2. **Construct Direct URL**
   - Combine the `ig_handle` with the Instagram URL template: `https://www.instagram.com/{ig_handle}/`.

3. **Run Scraper**
   - Use the `run_actor_sync_get_dataset_items` function to scrape data.
   - Pass the `directUrls` parameter and include the `last_fetched_date` (if available) in the query parameters to narrow the results.

4. **Store JSON Output Temporarily**
   - Save the scraper output to a temporary JSON file in a designated directory (e.g., `core/export/temp/`).

5. **Write Data to Database**
   - Parse the JSON file and write its contents to the database.
   - Use Django models to ensure data integrity.

6. **Delete Temporary JSON File**
   - Only delete the JSON file after successfully writing its contents to the database.

#### **Phase 2: Create Django View**
1. **Define the View**
   - Create a Django view (e.g., `refresh_scraper_view`) that:
     - Accepts a club identifier as input.
     - Triggers the scraper logic.
     - Returns a success or error response.

2. **Restrict Access**
   - Use Django’s `@login_required` and `@user_passes_test` decorators to restrict access to superusers (admins).

3. **Handle Last Fetched Date**
   - Query the database for the last fetched date of the club’s data.
   - Pass this date as a query parameter to the scraper to reduce token usage.

#### **Phase 3: Dashboard Integration**
1. **Add a Refresh Button**
   - Add a "Refresh Data" button to the admin dashboard for each club.
   - Link the button to the `refresh_scraper_view`.

2. **Display Last Fetched Date**
   - Show the last fetched date for each club in the dashboard.

3. **Handle Errors Gracefully**
   - Display error messages in the dashboard if the scraper fails.

---

## Future Roadmap

### **Search and Filter Mechanism for States and Universities**

#### **Objective**
Implement a unified search and filter mechanism for the states and universities page to enhance user experience and simplify navigation.

#### **Steps**
1. **Design and Implement Search Bar**
   - Add a search bar to the states and universities page.
   - Ensure the search bar can filter both states and universities dynamically based on user input.

2. **Backend Query Optimization**
   - Use Django ORM features like `annotate` and `prefetch_related` to optimize queries for filtering states and universities.
   - Ensure efficient database queries to handle large datasets.

3. **Frontend Integration**
   - Update the templates to display filtered results dynamically.
   - Ensure the search bar is styled consistently with the rest of the application.

4. **Testing and Validation**
   - Test the search and filter mechanism with various inputs to ensure accuracy and performance.
   - Validate that the feature works seamlessly across different devices and browsers.

#### **Future Enhancements**
- Add advanced filtering options (e.g., filter by state population, university type, etc.).
- Implement AJAX-based live search for real-time filtering without page reloads.

---

## Relevant Files
- `campushub/core/models.py` — Ensure the `Club` model has an `institution` field.
- `campushub/core/admin.py` — Add the `list_filter` attribute to the `ClubAdmin` class.
- `campushub/core/apify.py` — Refactor scraper logic.
- `campushub/core/views.py` — Add the `refresh_scraper_view`.
- `campushub/core/templates/admin/` — Update admin dashboard templates.

---

## Verification

### **Unit Tests**
1. Test the `institution` filter with valid and invalid values.
2. Test the scraper logic with valid and invalid `ig_handle` values.
3. Test database writes and ensure data integrity.
4. Test temporary JSON file creation and deletion.

### **Integration Tests**
1. Test the `refresh_scraper_view` with different clubs.
2. Verify that the view handles errors gracefully.

### **Manual Testing**
1. Log in as an admin user and test the filter functionality.
2. Use the admin dashboard to trigger the scraper and verify the data is updated in the database.

---

## Decisions

### **Institution Filter**
- Use Django’s default sidebar filter for now. Consider adding a search bar or dropdown in the future for enhanced usability.

### **Temporary JSON File Location**
- Use `core/export/temp/` for storing temporary files.

### **Access Control**
- Restrict scraper access to superusers for now.

### **Error Handling**
- Raise exceptions for scraper failures and log errors for debugging.

---

## Further Considerations

### **Future Enhancements**
1. Allow non-admin users to trigger the scraper with appropriate permissions.
2. Automate scraping at regular intervals using Django management commands.

### **Performance Optimization**
1. Cache the last fetched date to reduce database queries.
2. Optimize database writes for bulk operations.

### **Scalability**
1. Consider using Celery for asynchronous scraping tasks.