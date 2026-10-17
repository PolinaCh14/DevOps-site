Status: Approved

# Work Request Notifications — Current Repository Facts

## Notification model

- A notification has receiver and sender user foreign keys, a notification-type foreign key, message text, and creation date.
- The model's foreign-key deletion behavior differs by relation: receiver and type use `DO_NOTHING`; sender uses `CASCADE`.

## Work-request creation notification

- A `post_save` receiver for `WorkRequest` creates a notification only when `created=True`.
- The freelancer is used as sender, the owning project's user as receiver, and the message says a collaboration request was sent.
- The signal resolves notification type using `NotificationType.objects.get_or_create(id=1)`.
- It assumes that the work request has a freelancer and project and accesses their related records.

## Work-request update notification

- A separate `post_save` receiver returns for newly created requests and when the freelancer/user relation is missing.
- For every other save of an existing request, it creates a notification addressed to the freelancer, with the project's user as sender and the current status text in the message.
- It does not compare the saved status with the previous status. Thus, a save with no status change still creates a status-worded notification.
- Approval loops that save multiple requests invoke this behavior for each saved request.
- The receiver resolves notification type using `get_or_create(id=2)`.

## Email behavior

- A `post_save` receiver for `Notification` calls `send_notification_email` for each newly created notification.
- The notification app registers the signal module in `AppConfig.ready()`.
- The email function retrieves the notification and sends mail with `fail_silently=False`. It catches exceptions and prints them.
- This observed email path is part of the existing notification behavior; broader email/notification redesign is out of scope.

## Known limitations

- Update notifications are save-based, not confirmed-transition-based.
- No transition-specific notification policy exists in the inspected source.
- Multi-request approval saves may generate multiple freelancer notifications, including for requests that were already in a given state.
- Transaction-aware notification dispatch after a successful commit is not implemented in the inspected signal code.
