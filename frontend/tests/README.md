# Firestore authorization checks

Run from `frontend` with Node 22 and Java 21:

```sh
npm ci --ignore-scripts
npm run test:firestore-rules
```

The test command starts and stops a local Firestore emulator using the
`demo-easyoutfit-rules` project. The test refuses to run without an emulator.
It never loads production credentials or changes customer data.

`firestore.rules` is the only rules source. The frontend and backend deployment
configurations and emulator configuration point to it. The CI workflow runs a
configuration drift check and the emulator assertions on every pull request.
The backend rules file was removed to prevent independently deploying stale rules.

The suite proves client behavior only; Admin SDK operations bypass Firestore
rules and are covered separately by backend account, outfit, billing and credit
transaction tests. Roll out compatible API, worker and frontend changes before
publishing the rules. An application rollback must retain protected-field denial.
