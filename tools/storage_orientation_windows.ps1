Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$storageOrientationModule = New-Module -Name 'StorageOrientationWindows.FixedScope' -ScriptBlock {

$script:StorageSchemaVersion = 1
$script:StorageMaxDepth = 8
$script:StorageMaxEntries = 100000
$script:StorageWarningReasonCodes = @(
    'access_denied',
    'containment_rejected',
    'cross_device_skipped',
    'enumeration_failed',
    'max_depth_reached',
    'max_entries_reached',
    'metadata_unavailable',
    'mount_point_skipped',
    'protected_directory_skipped',
    'protected_file_skipped',
    'reparse_point_skipped',
    'symlink_skipped',
    'timestamp_unavailable',
    'unsupported_entry_type'
)
$script:StorageCollectorErrorCodes = @(
    'capacity_unavailable',
    'drive_not_fixed',
    'drive_not_ready',
    'elevated_execution_rejected',
    'known_folder_mismatch',
    'known_folder_unavailable',
    'root_not_allowlisted',
    'root_not_directory',
    'root_not_local',
    'root_unavailable',
    'unexpected_arguments'
)
$script:StorageProtectedDirectoryNames = @(
    '.aws',
    '.azure',
    '.gnupg',
    '.kube',
    '.password-store',
    '.secrets',
    '.ssh',
    '1password',
    'appdata',
    'bitwarden',
    'brave',
    'browser profiles',
    'chrome',
    'chromium',
    'credential manager',
    'credential-provider',
    'credential-providers',
    'credentials',
    'dashlane',
    'desktop',
    'documents',
    'edge',
    'firefox',
    'keepass',
    'keepassxc',
    'lastpass',
    'microsoft edge',
    'mozilla firefox',
    'opera',
    'opera gx stable',
    'opera stable',
    'passwords',
    'secrets',
    'google chrome'
)
$script:StorageProtectedFileNames = @(
    '.bash_history',
    '.lesshst',
    '.node_repl_history',
    '.python_history',
    '.sqlite_history',
    '.zsh_history',
    'consolehost_history.txt'
)
$script:StorageProtectedFileSuffixes = @('.key', '.p12', '.pem', '.pfx', '.ppk')
$script:StorageBackupSuffixes = @('.backup', '.bak', '.old', '.orig', '.save', '.swp', '.tmp', '~')

function Throw-StorageCollectorError {
    param([Parameter(Mandatory = $true)][string]$ReasonCode)

    if ($script:StorageCollectorErrorCodes -notcontains $ReasonCode) {
        throw [System.InvalidOperationException]::new('unbounded collector failure')
    }
    $exception = [System.InvalidOperationException]::new('bounded collector failure')
    $exception.Data['StorageReasonCode'] = $ReasonCode
    throw $exception
}

function New-StorageBaseRecord {
    param(
        [Parameter(Mandatory = $true)][string]$RecordType,
        [Parameter(Mandatory = $true)][string]$RootAlias,
        [Parameter(Mandatory = $true)][string]$RootKind
    )

    return [ordered]@{
        schema_version = $script:StorageSchemaVersion
        record_type = $RecordType
        collector = 'windows'
        root_alias = $RootAlias
        root_kind = $RootKind
    }
}

function New-StorageCapacityScopeRecord {
    param(
        [Parameter(Mandatory = $true)][long]$TotalBytes,
        [Parameter(Mandatory = $true)][long]$FreeBytes
    )

    $record = New-StorageBaseRecord -RecordType 'scope' -RootAlias 'windows_c' -RootKind 'capacity'
    $record['capacity_total_bytes'] = $TotalBytes
    $record['capacity_free_bytes'] = $FreeBytes
    return $record
}

function New-StorageTraversalScopeRecord {
    $record = New-StorageBaseRecord -RecordType 'scope' -RootAlias 'windows_downloads' -RootKind 'traversal'
    $record['capacity_total_bytes'] = $null
    $record['capacity_free_bytes'] = $null
    return $record
}

function New-StorageEntryRecord {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][ValidateSet('file', 'directory')][string]$EntryType,
        [Parameter(Mandatory = $true)][long]$SizeBytes,
        [AllowNull()][object]$ModifiedUtc
    )

    $record = New-StorageBaseRecord -RecordType 'entry' -RootAlias 'windows_downloads' -RootKind 'traversal'
    $record['relative_path'] = $RelativePath
    $record['entry_type'] = $EntryType
    $record['size_bytes'] = $SizeBytes
    if ($null -eq $ModifiedUtc) {
        $record['modified_utc'] = $null
    }
    else {
        $record['modified_utc'] = ([datetime]$ModifiedUtc).ToUniversalTime().ToString('o')
    }
    return $record
}

function New-StorageWarningRecord {
    param([Parameter(Mandatory = $true)][string]$ReasonCode)

    if ($script:StorageWarningReasonCodes -notcontains $ReasonCode) {
        throw [System.InvalidOperationException]::new('unbounded warning reason')
    }
    $record = New-StorageBaseRecord -RecordType 'warning' -RootAlias 'windows_downloads' -RootKind 'traversal'
    $record['reason_code'] = $ReasonCode
    return $record
}

function New-StorageCompletionRecord {
    param([Parameter(Mandatory = $true)][ValidateSet('complete', 'incomplete')][string]$ReasonCode)

    $record = New-StorageBaseRecord -RecordType 'completion' -RootAlias 'windows_downloads' -RootKind 'traversal'
    $record['reason_code'] = $ReasonCode
    return $record
}

function Test-StorageProtectedDirectoryName {
    param([Parameter(Mandatory = $true)][string]$Name)

    $caseFolded = $Name.ToLowerInvariant()
    if ($script:StorageProtectedDirectoryNames -contains $caseFolded) {
        return $true
    }
    $normalized = [Text.RegularExpressions.Regex]::Replace($caseFolded, '[\s._-]+', ' ').Trim()
    return $normalized -match '^(?:(?:google )?chrome(?: (?:user data|profiles?|profile .+))?|(?:mozilla )?firefox(?: (?:profiles?|profile .+))?|(?:microsoft )?edge(?: (?:user data|profiles?|profile .+))?|brave(?:software)?(?: (?:user data|profiles?|profile .+))?|opera(?: (?:gx stable|stable|profiles?|profile .+))?|1password(?: \d+)?|bitwarden(?: desktop)?|keepass(?:xc)?(?: (?:databases?|database .+|profiles?|profile .+))?|(?:dashlane|lastpass)(?: (?:profiles?|profile .+|vaults?|vault .+))?)$'
}

function Test-StorageProtectedFileName {
    param([Parameter(Mandatory = $true)][string]$Name)

    $normalized = $Name.ToLowerInvariant()
    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($suffix in $script:StorageBackupSuffixes) {
            if ($normalized.Length -gt $suffix.Length -and $normalized.EndsWith($suffix, [StringComparison]::Ordinal)) {
                $normalized = $normalized.Substring(0, $normalized.Length - $suffix.Length)
                $changed = $true
                break
            }
        }
    }
    if ($script:StorageProtectedFileNames -contains $normalized) {
        return $true
    }
    if ($normalized.StartsWith('id_', [StringComparison]::Ordinal)) {
        return $true
    }
    return $script:StorageProtectedFileSuffixes -contains [IO.Path]::GetExtension($normalized)
}

function Test-StorageElevated {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Assert-StorageNormalToken {
    param([AllowNull()][object]$IsElevatedOverride = $null)

    $isElevated = if ($null -eq $IsElevatedOverride) {
        Test-StorageElevated
    }
    else {
        [bool]$IsElevatedOverride
    }
    if ($isElevated) {
        Throw-StorageCollectorError -ReasonCode 'elevated_execution_rejected'
    }
}

function Get-StorageExpectedDownloadsRoot {
    return [IO.Path]::Combine('C:\', 'Users', 'acmen', 'Downloads')
}

function Resolve-StorageDownloadsKnownFolder {
    try {
        $shell = New-Object -ComObject Shell.Application
        $folder = $shell.Namespace('shell:Downloads')
        if ($null -eq $folder -or $null -eq $folder.Self) {
            Throw-StorageCollectorError -ReasonCode 'known_folder_unavailable'
        }
        return [string]$folder.Self.Path
    }
    catch {
        if ($_.Exception.Data.Contains('StorageReasonCode')) {
            throw
        }
        Throw-StorageCollectorError -ReasonCode 'known_folder_unavailable'
    }
}

function Assert-StorageExactRootPath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$ExpectedRoot
    )

    try {
        $canonicalRoot = [IO.Path]::GetFullPath($Root).TrimEnd('\')
        $canonicalExpected = [IO.Path]::GetFullPath($ExpectedRoot).TrimEnd('\')
    }
    catch {
        Throw-StorageCollectorError -ReasonCode 'root_not_allowlisted'
    }
    if ($canonicalRoot.StartsWith('\\', [StringComparison]::Ordinal)) {
        Throw-StorageCollectorError -ReasonCode 'root_not_local'
    }
    if (-not $canonicalRoot.Equals($canonicalExpected, [StringComparison]::OrdinalIgnoreCase)) {
        Throw-StorageCollectorError -ReasonCode 'root_not_allowlisted'
    }
    return $canonicalRoot
}

function Assert-StorageRootPreconditions {
    param([Parameter(Mandatory = $true)][string]$Root)

    $canonicalRoot = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $volumeRoot = [IO.Path]::GetPathRoot($canonicalRoot)
    $current = $volumeRoot.TrimEnd('\')
    $relativeComponents = $canonicalRoot.Substring($volumeRoot.Length).Split(
        @('\'),
        [StringSplitOptions]::RemoveEmptyEntries
    )
    try {
        foreach ($component in $relativeComponents) {
            $current = [IO.Path]::Combine($current + '\', $component)
            $attributes = [IO.File]::GetAttributes($current)
            if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                Throw-StorageCollectorError -ReasonCode 'root_not_directory'
            }
        }
        $attributes = [IO.File]::GetAttributes($canonicalRoot)
    }
    catch {
        if ($_.Exception.Data.Contains('StorageReasonCode')) {
            throw
        }
        Throw-StorageCollectorError -ReasonCode 'root_unavailable'
    }
    if (($attributes -band [IO.FileAttributes]::Directory) -eq 0) {
        Throw-StorageCollectorError -ReasonCode 'root_not_directory'
    }
    if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Throw-StorageCollectorError -ReasonCode 'root_not_directory'
    }
    return $canonicalRoot
}

function Assert-StorageExactRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$ExpectedRoot
    )

    $approvedPath = Assert-StorageExactRootPath -Root $Root -ExpectedRoot $ExpectedRoot
    return Assert-StorageRootPreconditions -Root $approvedPath
}

function Get-StorageFixedDrive {
    return [IO.DriveInfo]::new('C')
}

function Assert-StorageFixedReadyDrive {
    param(
        [Parameter(Mandatory = $true)][object]$Drive,
        [string]$ExpectedName = 'C:\'
    )

    if (-not ([string]$Drive.Name).Equals($ExpectedName, [StringComparison]::OrdinalIgnoreCase)) {
        Throw-StorageCollectorError -ReasonCode 'root_not_allowlisted'
    }
    if (-not [bool]$Drive.IsReady) {
        Throw-StorageCollectorError -ReasonCode 'drive_not_ready'
    }
    if ([string]$Drive.DriveType -ne 'Fixed') {
        Throw-StorageCollectorError -ReasonCode 'drive_not_fixed'
    }
}

function Get-StorageExceptionReason {
    param(
        [Parameter(Mandatory = $true)][Exception]$Exception,
        [switch]$Enumeration
    )

    $current = $Exception
    while ($null -ne $current.InnerException) {
        if ($current -is [UnauthorizedAccessException]) {
            break
        }
        $current = $current.InnerException
    }
    if ($current -is [UnauthorizedAccessException]) {
        return 'access_denied'
    }
    if ($Enumeration) {
        return 'enumeration_failed'
    }
    return 'metadata_unavailable'
}

function Invoke-StorageFixedDownloadsTraversal {
    if ($args.Count -ne 0) {
        Throw-StorageCollectorError -ReasonCode 'unexpected_arguments'
    }
    Assert-StorageNormalToken
    $resolvedDownloads = Resolve-StorageDownloadsKnownFolder
    $expectedDownloads = Get-StorageExpectedDownloadsRoot
    $approvedPath = Assert-StorageExactRootPath -Root $resolvedDownloads -ExpectedRoot $expectedDownloads
    if (-not $approvedPath.Equals($expectedDownloads, [StringComparison]::OrdinalIgnoreCase)) {
        Throw-StorageCollectorError -ReasonCode 'known_folder_mismatch'
    }
    try {
        $drive = Get-StorageFixedDrive
        Assert-StorageFixedReadyDrive -Drive $drive
    }
    catch {
        if ($_.Exception.Data.Contains('StorageReasonCode')) {
            throw
        }
        Throw-StorageCollectorError -ReasonCode 'capacity_unavailable'
    }
    $approvedRoot = Assert-StorageRootPreconditions -Root $approvedPath
    $MaximumDepth = $script:StorageMaxDepth
    $MaximumEntries = $script:StorageMaxEntries
    if ($MaximumDepth -lt 1 -or $MaximumEntries -lt 1) {
        throw [ArgumentOutOfRangeException]::new('collector bounds')
    }
    $rootPrefix = $approvedRoot.TrimEnd('\') + '\'
    $startingVolume = [IO.Path]::GetPathRoot($approvedRoot)
    $records = [Collections.Generic.List[object]]::new()
    $records.Add((New-StorageTraversalScopeRecord))
    $state = @{
        InspectionCount = 0
        WarningCount = 0
        Exhausted = $false
        Incomplete = $false
    }

    $addWarning = {
        param([string]$ReasonCode)
        $state.Incomplete = $true
        if ([int]$state.WarningCount -lt ($MaximumEntries + 1)) {
            $records.Add((New-StorageWarningRecord -ReasonCode $ReasonCode))
            $state.WarningCount = [int]$state.WarningCount + 1
        }
    }

    $getBoundedCandidates = {
        param([Parameter(Mandatory = $true)][System.Collections.IEnumerator]$Enumerator)

        $candidates = [Collections.Generic.List[string]]::new()
        try {
            while (-not [bool]$state.Exhausted) {
                try {
                    $hasCandidate = $Enumerator.MoveNext()
                    if (-not $hasCandidate) {
                        break
                    }
                    $candidate = [string]$Enumerator.Current
                }
                catch {
                    & $addWarning (Get-StorageExceptionReason -Exception $_.Exception -Enumeration)
                    break
                }
                $state.InspectionCount = [int]$state.InspectionCount + 1
                $candidates.Add($candidate)
                if ([int]$state.InspectionCount -ge $MaximumEntries) {
                    & $addWarning 'max_entries_reached'
                    $state.Exhausted = $true
                }
            }
        }
        finally {
            if ($Enumerator -is [IDisposable]) {
                $Enumerator.Dispose()
            }
        }
        $candidateArray = [string[]]$candidates.ToArray()
        [Array]::Sort($candidateArray, [StringComparer]::Ordinal)
        return $candidateArray
    }

    $visit = $null
    $visit = {
        param([string]$Directory, [int]$Depth)

        if ([bool]$state.Exhausted) {
            return
        }
        try {
            $directoryAttributes = [IO.File]::GetAttributes($Directory)
            if (($directoryAttributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                & $addWarning 'reparse_point_skipped'
                return
            }
        }
        catch {
            & $addWarning (Get-StorageExceptionReason -Exception $_.Exception -Enumeration)
            return
        }
        try {
            $enumerator = [IO.Directory]::EnumerateFileSystemEntries($Directory).GetEnumerator()
        }
        catch {
            & $addWarning (Get-StorageExceptionReason -Exception $_.Exception -Enumeration)
            return
        }
        $candidateArray = @(
            & $getBoundedCandidates $enumerator
        )

        foreach ($rawCandidate in $candidateArray) {
            try {
                $candidate = [IO.Path]::GetFullPath($rawCandidate)
            }
            catch {
                & $addWarning 'containment_rejected'
                continue
            }
            if (-not $candidate.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                & $addWarning 'containment_rejected'
                continue
            }
            if (-not ([IO.Path]::GetPathRoot($candidate)).Equals($startingVolume, [StringComparison]::OrdinalIgnoreCase)) {
                & $addWarning 'cross_device_skipped'
                continue
            }
            $candidateName = [IO.Path]::GetFileName($candidate)
            if (Test-StorageProtectedDirectoryName -Name $candidateName) {
                & $addWarning 'protected_directory_skipped'
                continue
            }
            if (Test-StorageProtectedFileName -Name $candidateName) {
                & $addWarning 'protected_file_skipped'
                continue
            }

            try {
                $attributes = [IO.File]::GetAttributes($candidate)
            }
            catch {
                & $addWarning (Get-StorageExceptionReason -Exception $_.Exception)
                continue
            }
            if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                & $addWarning 'reparse_point_skipped'
            }
            elseif (($attributes -band [IO.FileAttributes]::Directory) -ne 0) {
                try {
                    $metadata = [IO.DirectoryInfo]::new($candidate)
                    $relative = $candidate.Substring($rootPrefix.Length).Replace('\', '/')
                    $records.Add((New-StorageEntryRecord -RelativePath $relative -EntryType 'directory' -SizeBytes 0 -ModifiedUtc $metadata.LastWriteTimeUtc))
                    $childDepth = $Depth + 1
                    if ($childDepth -ge $MaximumDepth) {
                        & $addWarning 'max_depth_reached'
                    }
                    else {
                        $metadata.Refresh()
                        if (-not $metadata.Exists) {
                            & $addWarning 'metadata_unavailable'
                        }
                        elseif (($metadata.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                            & $addWarning 'reparse_point_skipped'
                        }
                        else {
                            & $visit $candidate $childDepth
                        }
                    }
                }
                catch {
                    & $addWarning (Get-StorageExceptionReason -Exception $_.Exception)
                }
            }
            elseif (($attributes -band [IO.FileAttributes]::Device) -eq 0) {
                try {
                    $metadata = [IO.FileInfo]::new($candidate)
                    $relative = $candidate.Substring($rootPrefix.Length).Replace('\', '/')
                    $records.Add((New-StorageEntryRecord -RelativePath $relative -EntryType 'file' -SizeBytes $metadata.Length -ModifiedUtc $metadata.LastWriteTimeUtc))
                }
                catch {
                    & $addWarning (Get-StorageExceptionReason -Exception $_.Exception)
                }
            }
            else {
                & $addWarning 'unsupported_entry_type'
            }

        }
    }

    & $visit $approvedRoot 0
    $completion = if ([bool]$state.Incomplete) { 'incomplete' } else { 'complete' }
    $records.Add((New-StorageCompletionRecord -ReasonCode $completion))
    return $records.ToArray()
}

function Invoke-StorageOrientationWindowsCollector {
    if ($args.Count -ne 0) {
        Throw-StorageCollectorError -ReasonCode 'unexpected_arguments'
    }
    $traversalRecords = @(Invoke-StorageFixedDownloadsTraversal)

    try {
        $drive = Get-StorageFixedDrive
        Assert-StorageFixedReadyDrive -Drive $drive
        $capacityRecord = New-StorageCapacityScopeRecord -TotalBytes $drive.TotalSize -FreeBytes $drive.AvailableFreeSpace
    }
    catch {
        if ($_.Exception.Data.Contains('StorageReasonCode')) {
            throw
        }
        Throw-StorageCollectorError -ReasonCode 'capacity_unavailable'
    }

    $records = [Collections.Generic.List[object]]::new()
    $records.Add($capacityRecord)
    foreach ($record in $traversalRecords) {
        $records.Add($record)
    }
    return $records.ToArray()
}

function Write-StorageJsonLines {
    param([Parameter(Mandatory = $true)][object[]]$Records)

    foreach ($record in $Records) {
        [Console]::Out.WriteLine(($record | ConvertTo-Json -Compress -Depth 3))
    }
}

Export-ModuleMember -Function Invoke-StorageOrientationWindowsCollector
}

if ($MyInvocation.InvocationName -eq '.') {
    Import-Module $storageOrientationModule -Global -Force
}
else {
    try {
        & $storageOrientationModule {
            param([int]$ArgumentCount)
            if ($ArgumentCount -ne 0) {
                Throw-StorageCollectorError -ReasonCode 'unexpected_arguments'
            }
            Write-StorageJsonLines -Records (Invoke-StorageOrientationWindowsCollector)
        } $args.Count
        exit 0
    }
    catch {
        $reasonCode = & $storageOrientationModule {
            param([Exception]$Exception)
            if ($Exception.Data.Contains('StorageReasonCode')) {
                $candidateReason = [string]$Exception.Data['StorageReasonCode']
                if ($script:StorageCollectorErrorCodes -contains $candidateReason) {
                    return $candidateReason
                }
            }
            return 'invalid_environment'
        } $_.Exception
        [Console]::Error.WriteLine("storage_orientation_error:$reasonCode")
        exit 2
    }
}

Remove-Variable -Name storageOrientationModule -ErrorAction SilentlyContinue
