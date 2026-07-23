# OTW Privacy Operations

This runbook turns the public privacy notice into repeatable operating steps. It contains no
credentials or personal information and may remain in the public source repository.

## Intake storage

- Public forms write only to the `otw-private-intake` Cloudflare Worker, its private
  `otw-private-intake` D1 database, and—only for rendered shirt-order artwork—the private
  `ORDER_ARTIFACTS` R2 bucket.
- Shirt orders also send an operational notification through the legacy Formspree endpoint.
  Treat the Formspree submission and resulting mailbox copy as part of the order record. Artwork
  download links in those notifications expire after 30 days; the underlying private R2 object
  remains subject to the order retention schedule.
- The intake Worker must not receive a GitHub token or write submissions to repository files.
- The four retired JSON ledger names in `.gitignore` must never be committed again.
- The daily Worker schedule permanently deletes records whose `retention_until` value has passed.

## Privacy requests

1. Monitor `ryandavid@outsidetheworld.com` for messages with an OTW privacy subject.
2. Acknowledge a request promptly and aim to complete it within 30 days. Check applicable law
   before denying a request or extending that period.
3. Ask only for the minimum information needed to match the requester to a record. Do not request
   government identification unless counsel determines that it is necessary.
4. Search all five D1 intake tables using normalized contact information. For shirt orders, also
   locate the matching private R2 object using `shirt_orders.artwork_key`, the corresponding
   Formspree submission, and the resulting notification email. Keep personal values out of shell
   history, source files, tickets, and logs; use a restricted temporary SQL file or the Cloudflare
   dashboard.
5. For access or portability, return only the requester's matching records through an agreed secure
   channel. Review free-text fields before disclosure.
6. For correction, update only the confirmed matching records. For deletion or unsubscribe, remove
   matching records from every applicable intake table and delete any matching private R2 artwork;
   do not merely hide them in the UI.
7. Record the request type, received/completed dates, status, and an opaque reference in
   `privacy_request_log`. Do not put the requester's email, message, or exported data in that log.
8. Confirm completion without exposing additional personal information.

## Retention and backups

- Waitlist and professional-inquiry records expire after two years.
- Support requests and seat check-ins expire after twelve months.
- Shirt-order records and private rendered artwork expire after two years. Delete corresponding
  Formspree submissions and notification emails on the same schedule.
- The scheduled Worker purge runs daily. Check its Cloudflare execution status at least monthly.
- Do not copy D1 exports into the public repository. Store any necessary backup in restricted,
  encrypted storage with an explicit deletion date.

## Incident response

If personal information is exposed or sent to the wrong place:

1. Stop new writes to the affected destination.
2. Preserve a restricted incident record and determine the data, people, and time period involved.
3. Remove public copies and rotate any exposed credentials.
4. Assess notification duties with qualified privacy counsel without delaying containment.
5. Document the cause, remediation, and safeguards added to prevent recurrence.

## Change checklist

Before changing a public form, storage provider, analytics tool, advertising integration, or app
data model:

- update the data inventory and retention rule;
- update the privacy notice before the new collection begins;
- obtain consent where required;
- test origin restrictions, error responses, and data destination;
- confirm personal data cannot enter Git history, client logs, or public APIs; and
- obtain counsel review for launches that materially expand data use, especially a public
  frgmnts app release.
