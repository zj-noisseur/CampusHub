There is a tendency for student clubs not limited to MMU only but rather generalisable across different institutions to manage and market their clubs exclusively on Instagram, which is overwhelmingly tuned and suited for images and certainly not text.

Many events like registrations for competitions, forums tend to be embedded in a QR code, and the links put in the caption are not clickable. Users have to go through the frustration of taking a screenshot, open in gallery and then from there open the link after OCR parsed the qr code, which is counter-intuitive.

The comprehensive list of all clubs and societies do exist and their associated Instagram accounts are readily available and accessible but unless a student have their friends on Instagram who are also added to any particular club, they would unlikely be able to be exposed to or even broadcasted to any of the latest updates and activities of the club. We understand that convincing people to switch to a text heavy platform is practically impossible due to their preference on Instagram or else Facebook would have been perfect, and creating yet another blog is also impossible as it would be a burden for groups and they would just stick with Instagram anyhow.


## Roles and Identities

- **No login**
  - Guest

- **Email verification** (MMU domain only for Phase 1)
  - General
  - Club admin
  - Club non-root admin
  - Admin (us)

## Pages

### Sign up Workflow
1. MMU email
2. Student name

### Admin Request
1. Upload image or PDF (organisational chart, signed letter)

### No Auth Needed Routes
1. **Landing page** (select institution — only MMU for first phase)
2. **Main feed** (all student clubs — claimed and unclaimed, filter by category)
3. **Club page** (organisational chart of past and present, scraped contents with filter)

### Protected Routes
1. **Admin workspace** (edit scraped contents, attendee view, certificate generation, batch send certificates)
2. **Personal dashboard** (attended events and upcoming ones)
3. **Root admin workspace** (leadership extension, leadership transfer)

## Features

### 1. Authentication

**User (Root Club Account Manager)**
- Upload leadership structure internal doc or Instagram post photo as proof
- Assign others (no limit, no proof needed) as non-root club managers
- Assigned members share the same validity period as the root admin
- Request extension, transfer, or leadership to existing non-root club manager or student

**User (Non-root Club Account Manager)**
- Request leadership transfer (requires approval from original root manager)

**Admin (us)**
- Approve or deny requests for claiming an account

### 2. Membership

**User** (must be from the same institution by default — MMU to MMU only, unless explicitly allowed)
- **Unlimited slots**:
  - Pay membership fee
    - Scan DuitNow QR
    - Upload proof of payment
    - Wait for approval
- **Limited slots**:
  - Express interest
  - Same approval workflow (payment not required)

**Club Admin**
- Approve or reject membership requests

### 3. Main Feed for Events Exploration (Instagram Scraper)

**All Users (including guests)**
- View scraped Instagram posts

### 4. Club Contents

**All Users**
- View organisation structure (current & past leadership)
- View scraped Instagram posts + manual modifications
- Filter posts by category: recruitment, competition, workshops, past events, misc (holiday announcement)
- Extract links from captions and QR codes from images (make them clickable)

**Club Account Manager**
- Edit scraped posts
- Publish and edit event details (location, time, date) — required upon claiming account
- Publish past events with photos and LLM-generated summaries
- Add list of club members

**General User**
- Express interest to join (name + WhatsApp number)
- Send join request email to all club managers
- View past events

**Guests**
- Can only view scraped posts
- No access to uploaded event photos (photos fetched from Google Drive)

### 5. Attendance

**Logged-in User**
- Scan QR code to check in (student email auto-recorded)

**Guest**
- Fill form with name, phone number, and email

**Club Account Manager**
- Upload pre-registered attendee list (for cross-referencing)
- View attendance dashboard with percentage breakdown

### 6. Certificate Generation

**Admin**
- Upload certificate design (JPG/PNG from Canva)
- Select center point for name placement
- System auto-previews with longest name from attendee list
- Confirm and batch send certificates via email

## Team Responsibilities

**Yuen Foong (Features 1 & 2)**
- User authentication and permissions
- Account claiming process
- Club membership & join requests

**Zi Jing (Features 3 & 4)**
- Main feed and club content display
- Parse QR codes from images
- Make Instagram caption links clickable
- Calendar view of upcoming events
- Display past event photos from Google Drive (for registered users)

**Zi Feng (Features 5 & 6)**
- Post-event housekeeping (certificate generation & batch sending)
- Admin dashboard for managing clubs
- Personal dashboard (past & upcoming events)