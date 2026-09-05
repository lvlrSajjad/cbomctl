---
name: Bug
about: Something behaves incorrectly
labels: bug
---

## What happened

## What you expected

## The CBOM

A minimal CycloneDX snippet that reproduces it. Redact freely — algorithm
names, `primitive`, `cryptoFunctions` and `oid` are usually all that matter.

## Command and output

```
cbomctl verdict ... 
```

## Was a purpose resolved incorrectly?

If so, include `cbomctl normalize <cbom>` output. A wrong *resolution* is a
more serious bug than a wrong verdict, because everything downstream depends
on it.
