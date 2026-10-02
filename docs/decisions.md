---

## Decision: Core Domain and Extension Boundaries

Ahead will distinguish between its core domain and optional integrations/extensions.

### Core domain

The initial core domain will contain concepts fundamental to Ahead's purpose:

- User
- Profile and preferences
- Personal context
- Task
- Event
- Goal
- Reminder
- Resource
- Actions and suggestions

These concepts should remain independent of specific third-party services.

### Extensions and integrations

Capabilities such as:

- Music
- External storage
- External calendars
- Voice services
- Third-party productivity services
- Future specialized services

will be treated as extensions or integrations rather than being embedded directly into the core domain.

### Reason

This separation allows new capabilities to be added without requiring major changes to the existing core system.

The core application should communicate with integrations through defined interfaces and service boundaries rather than tightly coupling domain entities to individual providers.

### AI boundary

AI will operate as an intelligence layer around the core domain.

AI may interpret, extract, classify, summarize, reason, and generate suggestions, but it will not directly control database persistence or bypass application validation and business rules.

The backend remains responsible for validating and executing application actions.

### Architectural principle

> Build the core around stable concepts and allow capabilities to be added around the core.

This decision is intended to reduce future maintenance and make the platform extensible without premature over-engineering.

## Reminder and Context Association

### Decision

For the current MVP, reminders remain independent database entities. A reminder will not directly contain nullable foreign keys such as `task_id` or `event_id`.

### Reason

A reminder may eventually relate to different types of personal context, including tasks, events, goals, resources, and other future domain objects. Adding separate nullable foreign keys for every possible type would make the Reminder model increasingly coupled to the expanding domain.

We will introduce the appropriate association mechanism when the Personal Context / Action layer is designed and the actual set of participating domain objects is established.

### Current Principle

Keep the Reminder model simple for the MVP while preserving the architecture needed for future context-aware reminders.

### Future Direction

The reminder system may later support escalation policies and multiple notification/action channels, such as phone notifications, sound, wearable haptics, and future hardware integrations. These capabilities should remain separate from the core Reminder entity.