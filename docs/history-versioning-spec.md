# History And Versioning Spec

## Goal

Expose the patient journey across consultations so the app stops feeling like isolated generators.

## MVP Scope

- consultation timeline by patient
- latest evaluation snapshot per consultation
- latest strategy snapshot per consultation
- latest meal plan snapshot per consultation
- deltas versus previous consultation for key tracking metrics

## Tracking Fields

- weight
- BMI
- maintenance energy
- target energy
- protein
- fat
- carbs

## Versioning Approach

- no new version tables in this phase
- existing records remain the source of truth
- the history view derives the latest artifact per consultation
- ordering is by consultation date and creation timestamp

## UI Expectations

- patient timeline in dashboard
- quick comparison against previous consultation
- clear display of meal plan status and completion

## Next Step

- add explicit version labels and compare selected plan versions side by side
