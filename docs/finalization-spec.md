# Finalization Spec

## Goal

Close the daily plan as a clinically reviewable artifact before PDF/export work.

## MVP Scope

- Persist meal plan lifecycle with `draft`, `reviewed`, `finalized`, `ready_for_export`
- Expose a consolidated final summary derived from:
  - patient
  - consultation
  - strategy goal
  - daily menu coverage
  - selected foods
  - finalized portions
  - plan notes
  - slot notes
- Block finalization if the plan still has pending slots

## Finalization Rules

- `reviewed`: internal review checkpoint, pending slots still allowed
- `finalized`: every slot must be selected
- `ready_for_export`: every slot must be selected and plan is considered presentation-ready

## Final Summary Output

- patient identification
- consultation date
- goal code
- meal pattern
- total targets vs selected totals
- completion status
- warnings
- per meal:
  - targets vs selected
  - pending slots
  - selected foods
  - final portions
  - slot notes

## Out Of Scope

- PDF generation
- share links
- printable templates
- multi-day exports
