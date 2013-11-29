`Webos.File` represents a file.

Listing files in the user's home folder :
```js
W.File.listDir('~', [function(files) { //We want to list files in the home folder (which is "~")
   var list = 'Files : ';
   for (var i = 0; i < files.length; i++) { //For each file
      var file = files[i];
      list += ' '+file.get('basename'); //Add the file to the list
   }
   alert(list); //Show the list
}, function(response) { //An error occured
   response.triggerError('Cannot list files in folder');
}]);
```


Since [1.0alpha1](../releases/tag/1.0alpha1).

# Methods

* **hydrate**(_Object_ **data**) : Update file's data, and complete automatically missing data.
 * _Object_ **data** The new data.
* **load**(_Webos.Callback_ **callback**) : Load this file's data.
 * _Webos.Callback_ **callback** The callback.
* **rename**(_String_ **newName**, _Webos.Callback_ **callback**) : Rename this file.
 * _String_ **newName** The new name for the file.
 * _Webos.Callback_ **callback** The callback.
* **remove**(_Webos.Callback_ **callback**) : Delete this file.
 * _Webos.Callback_ **callback** The callback.
* **readAsText**(_Webos.Callback_ **callback**) : Read this file's content as text.
 * _Webos.Callback_ **callback** The callback.
* **contents**(_Webos.Callback_ **callback**) : Get this file/directory's content.
 * _Webos.Callback_ **callback** The callback. If this file is a directory, an array of files will be provided.
* **getContents**() : Get this file/directory's content.
* **writeAsText**(_String_ **contents**, _Webos.Callback_ **callback**) : Write this file's content as text.
 * _String_ **contents** The new content for this file.
 * _Webos.Callback_ **callback** The callback.
* **setContents**(_String_ **contents**, _Webos.Callback_ **callback**) : Write this file's content as text.
 * _String_ **contents** The new content for this file.
 * _Webos.Callback_ **callback** The callback.
* **share**(_Webos.Callback_ **callback**) : Share this file and get the public URL.
 * _Webos.Callback_ **callback** The callback.
* _Boolean_ **can**(_String_ **auth**) : Check if the user can execute a given action on this file.
 * _String_ **auth** The name of the authorization. Can be "read" or "write".
* _Boolean_ **is**(_String_ **label**) : Check if this file has a given label.
 * _String_ **label** The label.
* _Boolean_ **checkAuthorization**(_String_ **auth**, _Webos.Callback_ **callback**) : Check if the user can execute a given action on this file. Trigger an error if not.
 * _String_ **auth** The name of the authorization. Can be "read" or "write".
 * _Webos.Callback_ **callback** The callback.
* **clearCache**() : Clear this file's cache.

# Static methods

* _Webos.File_ Webos.File.**get**(_String|Webos.File_ **file**, _Object_ **[data]**, _Boolean_ **[disableCache]**) : Get a file.
 * _String|Webos.File_ **file** The path to the file.
 * _Object_ **[data]** The file's data.
 * _Boolean_ **[disableCache]** If set to true, the file will not be stored in the cache.
* Webos.File.**load**(_String|Webos.File_ **path**, _Webos.Callback_ **callback**) : Load a file's metadata.
 * _String|Webos.File_ **path** The path to the file.
 * _Webos.Callback_ **callback** The callback.
* Webos.File.**listDir**(_String|Webos.File_ **path**, _Webos.Callback_ **callback**) : List a directory's files.
 * _String|Webos.File_ **path** The path to the directory.
 * _Webos.Callback_ **callback** The callback.
* Webos.File.**createFile**(_String|Webos.File_ **path**, _Webos.Callback_ **callback**) : Create an empty file.
 * _String|Webos.File_ **path** The path to the new file.
 * _Webos.Callback_ **callback** The callback.
* Webos.File.**createFolder**(_String|Webos.File_ **path**, _Webos.Callback_ **callback**) : Create a new folder.
 * _String|Webos.File_ **path** The path to the new folder.
 * _Webos.Callback_ **callback** The callback.
* Webos.File.**copy**(_Webos.File|String_ **source**, _Webos.File|String_ **dest**, _Webos.Callback_ **callback**) : Copy a file.
 * _Webos.File|String_ **source** The source file.
 * _Webos.File|String_ **dest** The destination file.
 * _Webos.Callback_ **callback** The callback.
* Webos.File.**move**(_Webos.File|String_ **source**, _Webos.File|String_ **dest**, _Webos.Callback_ **callback**) : Move a file.
 * _Webos.File|String_ **source** The source file.
 * _Webos.File|String_ **dest** The destination file.
 * _Webos.Callback_ **callback** The callback.
* Webos.File.**SearchResultItem**(_object_ **data**, _String|Webos.File_ **file**) : A search result item.
 * _object_ **data** The result data.
 * _String|Webos.File_ **file** The file.
* _Webos.Operation_ Webos.File.**search**(_object_ **options**, _Webos.Callback_ **callback**) : Search files.
 * _object_ **options** Search's options.
 * _Webos.Callback_ **callback** The callback.
* _Boolean_ Webos.File.**isCached**(_String|Webos.File_ **path**) : Check if a file is in the cache.
 * _String|Webos.File_ **path** The path to the file.
* Webos.File.**clearCache**(_String|Webos.File_ **[path]**, _Boolean_ **[clearParentCache]**) : Clear the cache.
 * _String|Webos.File_ **[path]** If specified, only the corresponding file's cache will be cleared.
 * _Boolean_ **[clearParentCache]** If set to true, the parent's cache will also be cleared.
* _String_ Webos.File.**cleanPath**(_String_ **path**) : Clean a path.
 * _String_ **path** The path to clean.
* _String_ Webos.File.**bytesToSize**(_Number_ **bytes**) : Convert a size in bytes to a human-readable file size (e.g. 1024 -> 1 Kio).
 * _Number_ **bytes** The size to convert.
* Webos.File.**mount**(_Webos.File.MountPoint_ **point**, _Webos.Callback_ **callback**) : Mount a device.
 * _Webos.File.MountPoint_ **point** The mount point.
 * _Webos.Callback_ **callback** The callback.
* _Object_ Webos.File.**mountedDevices**() : Get a list of mounted devices.
* _Webos.File.MountPoint_ Webos.File.**getMountData**(_String_ **local**) : Get a specific mount point, giving its local path.
 * _String_ **local** The mount point's local path.
* Webos.File.**umount**(_Webos.File.MountPoint_ **point**) : Umount a device.
 * _Webos.File.MountPoint_ **point** The mount point.
* Webos.File.**registerDriver**(_String_ **driverName**, _Object_ **data**) : Register a new file driver.
 * _String_ **driverName** The driver's name.
 * _Object_ **data** The driver's data.
* _Object_ Webos.File.**getDriverData**(_String_ **driverName**) : Get a driver's data, giving its name.
 * _String_ **driverName** The driver's name.
