# FUTURE_PLANS.md — FlowTrace Roadmap

## Phase 2: Real-Time Infrastructure

**Django Channels + WebSockets**
- Replace 10-second polling with live push updates
- Manager dashboard updates instantly when a developer switches tasks
- No frontend changes needed — swap `setInterval` fetch for WebSocket listener

**Redis**
- Session/cache layer for live status queries
- Celery task queue for async operations (email notifications, report generation)

## Phase 3: React Frontend

The API-first architecture means this is a frontend swap only:

- All `/api/*` endpoints remain unchanged
- Replace Django templates with a React SPA
- Add React Router for client-side navigation
- Use the same JWT auth flow

## Phase 4: Analytics & Intelligence

**Productivity Analytics**
- Context switch frequency per developer per day/week
- Average session duration per task type
- Interruption pattern analysis
- Focus time vs. fragmented time ratio

**AI-Powered Insights**
- Anomaly detection: "John switches tasks 3x more than usual today"
- Workload balance recommendations
- Sprint velocity prediction based on actual flow data

## Phase 5: Integrations

**GitHub Integration**
- Link tasks to commits/PRs
- Auto-detect task switches based on branch changes
- Enrich timeline with commit activity

**Slack Integration**
- Notify manager when developer switches tasks
- Daily workflow summary digest
- `/flowtrace status` slash command

**VS Code Extension**
- Auto-detect file changes and suggest task context
- One-click task switching from editor
- Idle detection

## Phase 6: Mobile

- React Native app for iOS/Android
- Quick task switching from phone
- Push notifications for @mentions
- Offline session logging with sync

## Phase 7: Advanced Features

**Sprint Reporting**
- Auto-generate sprint reports from actual activity data
- Compare planned vs. actual time distribution
- Export to PDF/CSV

**Team Patterns**
- Identify which developers are most interrupted
- Track which tasks cause the most context switches
- Manager intervention recommendations

**Multi-workspace Analytics**
- Organization-level productivity dashboard
- Cross-team comparison (anonymized)

## Architecture Evolution

```
Current:  Monolith Django + SQLite/PostgreSQL
Phase 2:  + Redis + Celery + Channels
Phase 3:  + React SPA (API unchanged)
Phase 4:  + Analytics service (separate Django app or microservice)
Phase 5:  + Integration webhooks
Phase 6:  + Mobile API (already REST-ready)
Phase 7:  + Data warehouse for historical analytics
```

The current architecture is designed to support all of these without a rewrite.
