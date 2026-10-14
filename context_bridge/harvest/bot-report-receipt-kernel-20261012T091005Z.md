# BOT REPORT: RECEIPT KERNEL V1 - 20261012T091005Z
- suite: signed-eventlog + env-hash + thermo-baseline + mistake-canary-CI

## 01-event.log
    [banked] event sealed sig=b16892aa647c

## 02-envhash.log
    [banked] env_hash=a3c02a8e9cd0594b212cfef620a8008099d898c675370d803bc49d4382514cb1

## 03-thermo.log
    [banked] bot_idle 8s source=rapl dram=0.54W; core=0.51W; package-0=0.73W; uncore=0.00W

## 04-mistake.log
    [gate] canary 0: JSONL parses (regression: generator-repr corruption)
      [banked] parse-ok
      [banked] no sticky CONFIRM flag
      [banked] no root-level leak files
      [held] history contains pasted-python traces (policy class)
      [banked] log free of generator-repr corruption
    [banked] canary CI v2: pass=4 fail=0 skipped=5 unique=4

## 05-validate.log
    rows=10 valid=10 bad=0

## Gate
- run dir: /home/jesse/openroot/logs/bot-receipt-kernel-20261012T091005Z
- report: /home/jesse/openroot/context_bridge/harvest/bot-report-receipt-kernel-20261012T091005Z.md
CANARY:BOT-RECEIPT-KERNEL-V1
