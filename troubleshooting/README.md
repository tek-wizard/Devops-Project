# Troubleshooting labs

Two deliberately broken manifests for practising common Kubernetes failures.
Both were tested and reproduce the symptoms described.

## Lab 1: broken-image.yaml (ImagePullBackOff)

The pod never reaches Running; it sits in ErrImagePull / ImagePullBackOff.

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl -n deskflow get pods -l app=broken-image
kubectl -n deskflow describe pod -l app=broken-image | tail -20
```

The Events section shows the pull failing because the tag
`deskflow-backend:does-not-exist` does not exist.

Fix: change the image to `deskflow-backend:local`, re-apply, confirm the pod
is Running, then `kubectl delete -f troubleshooting/broken-image.yaml`.

## Lab 2: broken-service.yaml (no Endpoints)

The Service exists but requests to it fail, because its selector
(`app: deskflow-bakend`, a typo) matches no pods.

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl -n deskflow get endpoints broken-service
kubectl -n deskflow describe svc broken-service
```

Fix: correct the selector to `app: deskflow-backend`, re-apply, and check
that `kubectl get endpoints broken-service` now lists pod IPs. Then
`kubectl delete -f troubleshooting/broken-service.yaml`.

These cover the two most common "deployed but not working" causes: a bad
image reference and a label/selector mismatch. Reading `kubectl describe`
Events and checking `Endpoints` handles a large share of real debugging.
