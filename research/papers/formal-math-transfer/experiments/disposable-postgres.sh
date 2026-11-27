#!/bin/sh
# Synthetic fixture only. Creates and removes its own container; accepts no database URL.
set -eu
test "$#" = 2 || { echo 'Usage: disposable-postgres.sh OLD_CHECKOUT NEW_CHECKOUT' >&2; exit 2; }
old=$(cd "$1" && pwd -P)
new=$(cd "$2" && pwd -P)
test "$(git -C "$old" rev-parse HEAD)" = d975846877b249bdce3314061a3b6341529e13b8
test "$(git -C "$new" rev-parse HEAD)" = 681ec80f1d5428b13a2ae13404af1e0af4f945e4
test -z "$(git -C "$old" status --porcelain)"
test -z "$(git -C "$new" status --porcelain)"
root=$(cd "$(dirname "$0")" && pwd -P)
# Use provider-assigned container identity, never operate on a pre-existing container.
id=$(docker run --rm -d -e POSTGRES_PASSWORD=synthetic-test -e POSTGRES_DB=dreaming_worker_contract -p 127.0.0.1::5432 postgres:17-alpine)
trap 'docker stop "$id" >/dev/null 2>&1 || true' EXIT
# Refuse any unexpected binding.
binding=$(docker port "$id" 5432/tcp)
case "$binding" in 127.0.0.1:*) ;; *) echo 'unexpected binding' >&2; exit 1;; esac
export PGPORT="${binding#127.0.0.1:}" PGHOST=127.0.0.1 PGUSER=postgres PGPASSWORD=synthetic-test PGDATABASE=dreaming_worker_contract
export THESEUS_DISPOSABLE_PG_BENCHMARK=yes
# Ignore external connection-service settings for this disposable fixture.
unset PGSERVICE PGSERVICEFILE PGOPTIONS PGHOSTADDR PGSSLROOTCERT PGSSLCERT PGSSLKEY
for i in $(seq 1 30); do if psql -X -Atqc 'SELECT 1' >/dev/null 2>&1; then break; fi; sleep 1; done
psql -X -v ON_ERROR_STOP=1 -Atqc 'SELECT 1' >/dev/null
psql -X -v ON_ERROR_STOP=1 -f "$new/qa/postgres/bootstrap-ledger-roles.sql" >&2
psql -X -v ON_ERROR_STOP=1 -f "$new/infra/postgres/dw_ledger_v1.sql" >&2
node "$root/postgres-benchmark.mjs" "$old" "$new"
docker stop "$id" >/dev/null
trap - EXIT
if docker inspect "$id" >/dev/null 2>&1; then echo 'disposable cleanup not confirmed' >&2; exit 1; fi
echo 'DISPOSABLE_DB_REMOVED' >&2
