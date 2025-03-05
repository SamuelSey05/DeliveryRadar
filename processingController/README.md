# Processing Controller

The processing controller is responsible for managing the processing threads that perform the speed analysis on the submitted videos. It is able to create and destroy processing threads, as well as distribute the data to such threads, and collect their returned outputs.

When the outputs are returned, it builds a structure containing the provided incident data, the ID and the speed, and sends this to the Data Storage.

---

## Passing to Processing Threads

The processing controller is able to pass the following to `ProcessingThread` objects via the `.process()` method

- Video Path
- ID
- Vehicle Type
