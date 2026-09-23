#!/bin/bash

set -eu
set -o pipefail
set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "$(readlink -f "${BASH_SOURCE[0]}")" )" &> /dev/null && pwd )
cd $SCRIPT_DIR/..

for YEAR in {2016..2025}; do
    for ACCUM in 1 3 24; do
        FILLEDACCUM=$(printf '%02d' $ACCUM)
        python -m obs_conversion.bom_rain_to_met \
            --stations /g/data/dp9/verification/data/jive-rain/StationData.csv \
            /g/data/dp9/verification/data/jive-rain/${YEAR}0101T0000Z-${YEAR}1231T2359Z-precipitation_accumulation-PT${FILLEDACCUM}H.nc \
            --output /g/data/dp9/verification/data/met/jive/precip/JIVE_APCP_A${ACCUM}_${YEAR}.nc
    done
done
