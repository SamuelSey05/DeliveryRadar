# Common 

This directory is essentially a local Library of code to be used across components, documented below:

## vehicle_type

### `VehicleType`

This is an enumeration class used to denote the type of a Vehicle in a submission

## package_hashing

### `hashFile()`

This is a function that returns an sha256 hash of a given file. Use this for consistency across the project.

## check_dict

### `checkClass()`

This is a function that can be used to check if an object is an instance of a given class, used particularly below for TypedDicts

### `checkIncident()`

This is a function used to check if a given incident dict is formatted correctly with the correct fields

## db_types

### `LatLon`

This is a class used to specify the type of a location stored as a latitude-longitude pair.

### `W3W` 

This is a class used to specify the type of a location stored in a What3Words compatible form. This was planned to be used early in development but was deprecated in favour of `LatLon`

### `locationClass`

Value used as one of the above to specify the location format. This allowed a replacement without major rewrites.

### `DBRow`

This class specifies a row returned from the database for responding to an API call.

### `prepDBRows()`

This changes a `DBRow` into a serialisable JSON dict format.

### `DBConnectionFailure`

This is the exception raised when the database fails to connect.

## processing_data

### `processingArgs`

This is the type specification of the arguments passed to a Processing Thread.

### `SIG_END`

This is the definition of the signal passed to a process to break it's processing loop. See usage in ProcessingThreads and ProcessingController.

## tempdir

### `TempDir`

This class creates a temporary storage location in the system temporary location (`/tmp` on UNIX). It manages the deletion of this tempfile on clean exit.

## unzip

### `unzip`

This function extracts the contents of a zipfile to it's current directory.

## zipErrors

### `SubmissionError`

This is the error raised when a submission fails to parse - one or more files or values are missing.

### `CannotMoveZip`

This is the error raised in place of an OSError if the moving of a zip file fails.

## zipspec

### `videoExtensions`

This is a list denoting the valid video extensions of a submitted video.

### `jsonDate`

Specifies the format of a Date in the submitted JSON file.

### `jsonTime`

Similarly, specifies the format of a Time in the submitted JSON file.

### `Incident`

Specifies the overall format of the submitted `incident.json`

### `datetimeFromIncident()`

This function returns the Date and Time in the `incident.json` as a DateTime object.