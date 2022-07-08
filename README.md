# Safeway Clipper

A time saving python script for auto clipping safeway deals and coupons.

[![Run Safeway Coupons Clipper](../../actions/workflows/run-safeway-clipper.yml/badge.svg)](../../actions/workflows/run-safeway-clipper.yml)

## Start Clipping

1. [Fork](https://github.com/shadowwalker/safeway-clipper/fork) this repository
2. [Create](https://github.com/settings/tokens/new) a new personal access token (PAT), set expiration to `No expiration`.
3. [Setup secrets](../../settings/secrets/actions) in your forked repository Settings tab -> Secrets Menu -> Actions with exact secret names below:
   1. `GH_TOKEN`: `<PAT you created in step 2>`
   2. `SAFEWAY_LOGIN_EMAIL`: `<Your safeway login email>`
   3. `SAFEWAY_LOGIN_PASSWORD`: `<Your safeway login password>`
4. Done! Automatically clipping start at `6AM` everyday. Check [Actions tab](../../actions/workflows/run-safeway-clipper.yml) for status.
