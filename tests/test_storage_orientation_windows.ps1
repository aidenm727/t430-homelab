Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $repositoryRoot 'tools\storage_orientation_windows.ps1')
$collectorSource = [IO.File]::ReadAllText((Join-Path $repositoryRoot 'tools\storage_orientation_windows.ps1'))

$global:StorageAssertions = 0
$global:StorageSkipped = 0

function global:Assert-StorageTrue {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    $global:StorageAssertions++
    if (-not $Condition) {
        throw [InvalidOperationException]::new($Message)
    }
}

function global:Assert-StorageEqual {
    param(
        [AllowNull()][object]$Expected,
        [AllowNull()][object]$Actual,
        [Parameter(Mandatory = $true)][string]$Message
    )
    $global:StorageAssertions++
    if ($Expected -ne $Actual) {
        throw [InvalidOperationException]::new("$Message expected=[$Expected] actual=[$Actual]")
    }
}

function global:Assert-StorageThrowsReason {
    param(
        [Parameter(Mandatory = $true)][scriptblock]$Action,
        [Parameter(Mandatory = $true)][string]$ReasonCode
    )
    $global:StorageAssertions++
    try {
        & $Action
    }
    catch {
        $actual = [string]$_.Exception.Data['StorageReasonCode']
        if ($actual -ne $ReasonCode) {
            throw [InvalidOperationException]::new("wrong bounded reason expected=[$ReasonCode] actual=[$actual]")
        }
        return
    }
    throw [InvalidOperationException]::new("expected bounded failure [$ReasonCode]")
}

function global:Get-RecordTypes {
    param([object[]]$Records)
    return @($Records | ForEach-Object { [string]$_.record_type })
}

class StoragePartialFailureEnumerator : System.Collections.IEnumerator {
    [object[]]$Values
    [int]$Position = -1
    [int]$MoveNextCalls = 0

    StoragePartialFailureEnumerator([object[]]$Values) {
        $this.Values = $Values
    }

    [object] get_Current() {
        return $this.Values[$this.Position]
    }

    [bool] MoveNext() {
        $this.MoveNextCalls++
        if (($this.Position + 1) -ge $this.Values.Count) {
            throw [IO.IOException]::new('synthetic enumerator failure')
        }
        $this.Position++
        return $true
    }

    [void] Reset() {
        $this.Position = -1
        $this.MoveNextCalls = 0
    }
}

function global:New-StorageSyntheticModule {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$FixedRoot,
        [Parameter(Mandatory = $true)][string]$ModuleSuffix,
        [bool]$IsElevated = $false,
        [string]$ResolvedDownloadsRoot = '',
        [switch]$KnownFolderUnavailable,
        [bool]$DriveReady = $true,
        [string]$DriveType = 'Fixed',
        [switch]$InstrumentTraversal
    )

    $syntheticModuleName = "StorageOrientationWindows.SyntheticFixedScope.$ModuleSuffix"
    $syntheticCommandName = "Invoke-StorageOrientationWindowsSyntheticCollector$ModuleSuffix"
    $sourceCopy = $Source.Replace(
        'StorageOrientationWindows.FixedScope',
        $syntheticModuleName
    ).Replace(
        'Invoke-StorageOrientationWindowsCollector',
        $syntheticCommandName
    )
    $tokens = $null
    $parseErrors = $null
    $ast = [Management.Automation.Language.Parser]::ParseInput(
        $sourceCopy,
        [ref]$tokens,
        [ref]$parseErrors
    )
    Assert-StorageEqual 0 @($parseErrors).Count 'production source must parse before test-owned cloning'
    $literalRoot = $FixedRoot.Replace("'", "''")
    $resolvedDownloads = if ([string]::IsNullOrWhiteSpace($ResolvedDownloadsRoot)) {
        $FixedRoot
    }
    else {
        $ResolvedDownloadsRoot
    }
    $literalResolvedDownloads = $resolvedDownloads.Replace("'", "''")
    $literalDriveType = $DriveType.Replace("'", "''")
    $isElevatedLiteral = if ($IsElevated) { '$true' } else { '$false' }
    $driveReadyLiteral = if ($DriveReady) { '$true' } else { '$false' }
    $knownFolderFunction = if ($KnownFolderUnavailable) {
        "function Resolve-StorageDownloadsKnownFolder { Throw-StorageCollectorError -ReasonCode 'known_folder_unavailable' }"
    }
    else {
        "function Resolve-StorageDownloadsKnownFolder { return '$literalResolvedDownloads' }"
    }
    $fixedDriveFunction = if ($InstrumentTraversal) {
        "function Get-StorageFixedDrive { `$script:StorageTestDriveConstructions++; return [pscustomobject]@{ Name = 'C:\'; IsReady = $driveReadyLiteral; DriveType = '$literalDriveType'; TotalSize = 1000; AvailableFreeSpace = 250 } }"
    }
    else {
        "function Get-StorageFixedDrive { return [pscustomobject]@{ Name = 'C:\'; IsReady = $driveReadyLiteral; DriveType = '$literalDriveType'; TotalSize = 1000; AvailableFreeSpace = 250 } }"
    }
    $testFunctions = @{
        'Test-StorageElevated' = "function Test-StorageElevated { return $isElevatedLiteral }"
        'Get-StorageExpectedDownloadsRoot' = "function Get-StorageExpectedDownloadsRoot { return '$literalRoot' }"
        'Resolve-StorageDownloadsKnownFolder' = $knownFolderFunction
        'Get-StorageFixedDrive' = $fixedDriveFunction
    }
    $replacements = [Collections.Generic.List[object]]::new()
    foreach ($name in $testFunctions.Keys) {
        $definition = @(
            $ast.FindAll(
                {
                    param($node)
                    $node -is [Management.Automation.Language.FunctionDefinitionAst] -and
                        $node.Name -eq $name
                },
                $true
            )
        )
        Assert-StorageEqual 1 $definition.Count "test clone must find one function: $name"
        $replacements.Add([pscustomobject]@{
            Start = $definition[0].Extent.StartOffset
            End = $definition[0].Extent.EndOffset
            Text = $testFunctions[$name]
        })
    }
    foreach ($replacement in @($replacements | Sort-Object Start -Descending)) {
        $sourceCopy = $sourceCopy.Substring(0, $replacement.Start) +
            $replacement.Text +
            $sourceCopy.Substring($replacement.End)
    }
    if ($InstrumentTraversal) {
        $instrumentation = @(
            [pscustomobject]@{
                Target = '                    $hasCandidate = $Enumerator.MoveNext()'
                Replacement = "                    `$script:StorageTestEnumeratorAdvancements++`n                    `$hasCandidate = `$Enumerator.MoveNext()"
            },
            [pscustomobject]@{
                Target = '            $enumerator = [IO.Directory]::EnumerateFileSystemEntries($Directory).GetEnumerator()'
                Replacement = "            `$script:StorageTestEnumeratorCreations++`n            `$enumerator = [IO.Directory]::EnumerateFileSystemEntries(`$Directory).GetEnumerator()"
            },
            [pscustomobject]@{
                Target = '            $attributes = [IO.File]::GetAttributes($current)'
                Replacement = "            `$script:StorageTestRootMetadataAccesses++`n            `$attributes = [IO.File]::GetAttributes(`$current)"
            },
            [pscustomobject]@{
                Target = '        $attributes = [IO.File]::GetAttributes($canonicalRoot)'
                Replacement = "        `$script:StorageTestRootMetadataAccesses++`n        `$attributes = [IO.File]::GetAttributes(`$canonicalRoot)"
            },
            [pscustomobject]@{
                Target = '            $directoryAttributes = [IO.File]::GetAttributes($Directory)'
                Replacement = "            `$script:StorageTestRootMetadataAccesses++`n            `$directoryAttributes = [IO.File]::GetAttributes(`$Directory)"
            },
            [pscustomobject]@{
                Target = '                $attributes = [IO.File]::GetAttributes($candidate)'
                Replacement = "                `$script:StorageTestCandidateMetadataAccesses++`n                `$attributes = [IO.File]::GetAttributes(`$candidate)"
            }
        )
        foreach ($probe in $instrumentation) {
            Assert-StorageEqual 1 ([Text.RegularExpressions.Regex]::Matches(
                $sourceCopy,
                [Text.RegularExpressions.Regex]::Escape($probe.Target)
            )).Count 'test-owned ordering probe must match exactly one production operation'
            $sourceCopy = $sourceCopy.Replace($probe.Target, $probe.Replacement)
        }
    }
    . ([scriptblock]::Create($sourceCopy))
    $syntheticCommand = Get-Command $syntheticCommandName -CommandType Function -ErrorAction Stop
    $syntheticModule = $syntheticCommand.Module
    if ($InstrumentTraversal) {
        & $syntheticModule {
            $script:StorageTestDriveConstructions = 0
            $script:StorageTestEnumeratorCreations = 0
            $script:StorageTestEnumeratorAdvancements = 0
            $script:StorageTestRootMetadataAccesses = 0
            $script:StorageTestCandidateMetadataAccesses = 0
        }
    }
    return $syntheticModule
}

function global:Assert-StoragePreEnumerationGateStopsTraversal {
    param(
        [Parameter(Mandatory = $true)][System.Management.Automation.PSModuleInfo]$Module,
        [Parameter(Mandatory = $true)][string]$ExportedCommandName,
        [Parameter(Mandatory = $true)][string]$ReasonCode,
        [Parameter(Mandatory = $true)][int]$ExpectedDriveConstructions,
        [Parameter(Mandatory = $true)][bool]$InvokePrivate
    )

    & $Module {
        $script:StorageTestDriveConstructions = 0
        $script:StorageTestEnumeratorCreations = 0
        $script:StorageTestEnumeratorAdvancements = 0
        $script:StorageTestRootMetadataAccesses = 0
        $script:StorageTestCandidateMetadataAccesses = 0
    }
    if ($InvokePrivate) {
        Assert-StorageThrowsReason -ReasonCode $ReasonCode -Action {
            & $Module { Invoke-StorageFixedDownloadsTraversal | Out-Null }
        }
    }
    else {
        $exportedCommand = Get-Command $ExportedCommandName -CommandType Function -ErrorAction Stop
        Assert-StorageThrowsReason -ReasonCode $ReasonCode -Action {
            & $exportedCommand | Out-Null
        }
    }
    $observed = & $Module {
        return [pscustomobject]@{
            DriveConstructions = $script:StorageTestDriveConstructions
            EnumeratorCreations = $script:StorageTestEnumeratorCreations
            EnumeratorAdvancements = $script:StorageTestEnumeratorAdvancements
            RootMetadataAccesses = $script:StorageTestRootMetadataAccesses
            CandidateMetadataAccesses = $script:StorageTestCandidateMetadataAccesses
        }
    }
    $surface = if ($InvokePrivate) { 'direct private traversal' } else { 'exported collector traversal' }
    Assert-StorageEqual $ExpectedDriveConstructions $observed.DriveConstructions "$surface must construct the fixed drive only after earlier gates"
    Assert-StorageEqual 0 $observed.EnumeratorCreations "$surface must reject before enumerator creation"
    Assert-StorageEqual 0 $observed.EnumeratorAdvancements "$surface must reject before enumerator advancement"
    Assert-StorageEqual 0 $observed.RootMetadataAccesses "$surface must reject before root filesystem metadata access"
    Assert-StorageEqual 0 $observed.CandidateMetadataAccesses "$surface must reject before candidate metadata access"
}

$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('g14-storage-orientation-' + [Guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($testRoot) | Out-Null

try {
    $collectorCommand = Get-Command 'Invoke-StorageOrientationWindowsCollector' -CommandType Function -ErrorAction SilentlyContinue
    Assert-StorageTrue ($null -ne $collectorCommand) 'fixed production entry must be exported'
    $collectorModule = $collectorCommand.Module
    Assert-StorageTrue ($collectorModule -is [System.Management.Automation.PSModuleInfo]) 'exported fixed entry must identify one invokable module object'
    Assert-StorageEqual 'StorageOrientationWindows.FixedScope' $collectorModule.Name 'exported fixed entry must belong to the fixed-scope module'
    Assert-StorageTrue ($null -eq (Get-Command 'Invoke-StorageTraversalCore' -ErrorAction SilentlyContinue)) 'arbitrary-root traversal core must not be exported by dot-sourcing'
    Assert-StorageTrue ($null -eq (Get-Command 'Assert-StorageNormalToken' -ErrorAction SilentlyContinue)) 'elevation test seam must not be exported by dot-sourcing'
    $privateArbitraryRootAvailable = & $collectorModule {
        return $null -ne (Get-Command 'Invoke-StorageTraversalCore' -CommandType Function -ErrorAction SilentlyContinue)
    }
    Assert-StorageTrue (-not $privateArbitraryRootAvailable) 'production module scope must not retain the arbitrary-root traversal core'
    $privateEnumeratorSurfaceAvailable = & $collectorModule {
        return $null -ne (Get-Command 'Get-StorageBoundedCandidates' -CommandType Function -ErrorAction SilentlyContinue)
    }
    Assert-StorageTrue (-not $privateEnumeratorSurfaceAvailable) 'production module scope must not retain a caller-supplied enumerator collector'
    $productionEnumerationCommands = @(& $collectorModule {
        param([string]$ProductionModuleName)

        Get-Command -CommandType Function | Where-Object {
            $_.ModuleName -eq $ProductionModuleName -and
                $_.Definition.Contains('EnumerateFileSystemEntries')
        } | ForEach-Object {
            [pscustomobject]@{
                Name = $_.Name
                HasRootParameter = $_.Parameters.ContainsKey('Root')
                HasExpectedRootParameter = $_.Parameters.ContainsKey('ExpectedRoot')
                Definition = $_.Definition
            }
        }
    } $collectorModule.Name)
    Assert-StorageTrue ($productionEnumerationCommands.Count -gt 0) 'test must identify every production module-owned direct filesystem enumeration capability'
    Assert-StorageTrue ($productionEnumerationCommands.Name -contains 'Invoke-StorageFixedDownloadsTraversal') 'fixed Downloads traversal must remain a recognized production enumeration capability'
    foreach ($enumerationCommand in $productionEnumerationCommands) {
        Assert-StorageTrue (-not $enumerationCommand.HasRootParameter) "$($enumerationCommand.Name) must not accept a root parameter"
        Assert-StorageTrue (-not $enumerationCommand.HasExpectedRootParameter) "$($enumerationCommand.Name) must not accept an expected-root parameter"
        Assert-StorageTrue ($enumerationCommand.Definition.Contains('Assert-StorageNormalToken')) "$($enumerationCommand.Name) must contain its normal-token gate"
        Assert-StorageTrue ($enumerationCommand.Definition.Contains('Resolve-StorageDownloadsKnownFolder')) "$($enumerationCommand.Name) must resolve Downloads internally"
        Assert-StorageTrue ($enumerationCommand.Definition.Contains('Get-StorageExpectedDownloadsRoot')) "$($enumerationCommand.Name) must obtain the fixed approved root internally"
        Assert-StorageTrue ($enumerationCommand.Definition.Contains('Assert-StorageExactRootPath')) "$($enumerationCommand.Name) must validate the exact resolved pathname before drive inspection"
        Assert-StorageTrue ($enumerationCommand.Definition.Contains('Get-StorageFixedDrive')) "$($enumerationCommand.Name) must construct the fixed production drive internally"
        Assert-StorageTrue ($enumerationCommand.Definition.Contains('Assert-StorageFixedReadyDrive')) "$($enumerationCommand.Name) must contain its fixed and ready drive gate"
        Assert-StorageTrue ($enumerationCommand.Definition.Contains('Assert-StorageRootPreconditions')) "$($enumerationCommand.Name) must retain root and reparse preconditions"
        $normalTokenIndex = $enumerationCommand.Definition.IndexOf('Assert-StorageNormalToken', [StringComparison]::Ordinal)
        $knownFolderIndex = $enumerationCommand.Definition.IndexOf('Resolve-StorageDownloadsKnownFolder', [StringComparison]::Ordinal)
        $expectedRootIndex = $enumerationCommand.Definition.IndexOf('Get-StorageExpectedDownloadsRoot', [StringComparison]::Ordinal)
        $exactPathIndex = $enumerationCommand.Definition.IndexOf('Assert-StorageExactRootPath', [StringComparison]::Ordinal)
        $fixedDriveIndex = $enumerationCommand.Definition.IndexOf('Get-StorageFixedDrive', [StringComparison]::Ordinal)
        $driveGateIndex = $enumerationCommand.Definition.IndexOf('Assert-StorageFixedReadyDrive', [StringComparison]::Ordinal)
        $rootPreconditionsIndex = $enumerationCommand.Definition.IndexOf('Assert-StorageRootPreconditions', [StringComparison]::Ordinal)
        $enumerationIndex = $enumerationCommand.Definition.IndexOf('EnumerateFileSystemEntries', [StringComparison]::Ordinal)
        $candidateMetadataIndex = $enumerationCommand.Definition.IndexOf('$attributes = [IO.File]::GetAttributes($candidate)', [StringComparison]::Ordinal)
        Assert-StorageTrue (
            0 -le $normalTokenIndex -and
                $normalTokenIndex -lt $knownFolderIndex -and
                $knownFolderIndex -lt $expectedRootIndex -and
                $expectedRootIndex -lt $exactPathIndex -and
                $exactPathIndex -lt $fixedDriveIndex -and
                $fixedDriveIndex -lt $driveGateIndex -and
                $driveGateIndex -lt $rootPreconditionsIndex -and
                $rootPreconditionsIndex -lt $enumerationIndex -and
                $enumerationIndex -lt $candidateMetadataIndex
        ) "$($enumerationCommand.Name) gate order must be normal token, known folder, fixed expected root, exact path, fixed drive construction, ready/fixed gate, root preconditions, enumeration, then candidate metadata"
        Assert-StorageTrue (
            $enumerationCommand.Definition.IndexOf('Test-StorageProtectedFileName', [StringComparison]::Ordinal) -lt
                $candidateMetadataIndex
        ) "$($enumerationCommand.Name) must reject protected filenames before candidate metadata access"
    }
    $fixedGateShapes = & $collectorModule {
        return [pscustomobject]@{
            ExpectedRoot = (Get-Command 'Get-StorageExpectedDownloadsRoot' -CommandType Function -ErrorAction Stop).Definition
            FixedDrive = (Get-Command 'Get-StorageFixedDrive' -CommandType Function -ErrorAction Stop).Definition
            DriveGate = (Get-Command 'Assert-StorageFixedReadyDrive' -CommandType Function -ErrorAction Stop).Definition
        }
    }
    Assert-StorageTrue ($fixedGateShapes.ExpectedRoot.Contains("[IO.Path]::Combine('C:\', 'Users', 'acmen', 'Downloads')")) 'production expected root must remain the fixed approved Downloads pathname'
    Assert-StorageTrue ($fixedGateShapes.FixedDrive.Contains("[IO.DriveInfo]::new('C')")) 'production drive construction must remain fixed to C:'
    $driveNameGateIndex = $fixedGateShapes.DriveGate.IndexOf('$Drive.Name', [StringComparison]::Ordinal)
    $driveReadyGateIndex = $fixedGateShapes.DriveGate.IndexOf('$Drive.IsReady', [StringComparison]::Ordinal)
    $driveTypeGateIndex = $fixedGateShapes.DriveGate.IndexOf('$Drive.DriveType', [StringComparison]::Ordinal)
    Assert-StorageTrue (
        0 -le $driveNameGateIndex -and
            $driveNameGateIndex -lt $driveReadyGateIndex -and
            $driveReadyGateIndex -lt $driveTypeGateIndex
    ) 'fixed drive gate must reject non-C:, not-ready, then non-fixed drives before traversal'
    Assert-StorageTrue ($collectorCommand.Definition.Contains('Invoke-StorageFixedDownloadsTraversal')) 'exported collector must reach filesystem enumeration only through the gated fixed traversal'
    & $collectorModule {
        Assert-StorageThrowsReason -ReasonCode 'unexpected_arguments' -Action {
            Invoke-StorageFixedDownloadsTraversal 'synthetic-root-bypass' | Out-Null
        }
    }
    Assert-StorageThrowsReason -ReasonCode 'unexpected_arguments' -Action {
        Invoke-StorageOrientationWindowsCollector 'synthetic-root-bypass' | Out-Null
    }

    $preEnumerationGateCases = @(
        [pscustomobject]@{ Suffix = 'Elevated'; Arguments = @{ IsElevated = $true }; ReasonCode = 'elevated_execution_rejected'; DriveConstructions = 0 },
        [pscustomobject]@{ Suffix = 'KnownFolderUnavailable'; Arguments = @{ KnownFolderUnavailable = $true }; ReasonCode = 'known_folder_unavailable'; DriveConstructions = 0 },
        [pscustomobject]@{ Suffix = 'ExactRootMismatch'; Arguments = @{ ResolvedDownloadsRoot = (Join-Path $testRoot 'not-the-fixed-root') }; ReasonCode = 'root_not_allowlisted'; DriveConstructions = 0 },
        [pscustomobject]@{ Suffix = 'NotReady'; Arguments = @{ DriveReady = $false; DriveType = 'Fixed' }; ReasonCode = 'drive_not_ready'; DriveConstructions = 1 },
        [pscustomobject]@{ Suffix = 'NotFixed'; Arguments = @{ DriveReady = $true; DriveType = 'Network' }; ReasonCode = 'drive_not_fixed'; DriveConstructions = 1 }
    )
    foreach ($gateCase in $preEnumerationGateCases) {
        $probeArguments = @{
            Source = $collectorSource
            FixedRoot = $testRoot
            ModuleSuffix = $gateCase.Suffix
            InstrumentTraversal = $true
        }
        foreach ($argument in $gateCase.Arguments.GetEnumerator()) {
            $probeArguments[$argument.Key] = $argument.Value
        }
        $probeModule = New-StorageSyntheticModule @probeArguments
        $probeCommandName = "Invoke-StorageOrientationWindowsSyntheticCollector$($gateCase.Suffix)"
        Assert-StoragePreEnumerationGateStopsTraversal -Module $probeModule -ExportedCommandName $probeCommandName -ReasonCode $gateCase.ReasonCode -ExpectedDriveConstructions $gateCase.DriveConstructions -InvokePrivate $true
        Assert-StoragePreEnumerationGateStopsTraversal -Module $probeModule -ExportedCommandName $probeCommandName -ReasonCode $gateCase.ReasonCode -ExpectedDriveConstructions $gateCase.DriveConstructions -InvokePrivate $false
    }

    $syntheticCollectorModule = New-StorageSyntheticModule -Source $collectorSource -FixedRoot $testRoot -ModuleSuffix 'HappyPath'
    Assert-StorageEqual 'StorageOrientationWindows.SyntheticFixedScope.HappyPath' $syntheticCollectorModule.Name 'synthetic roots must run only in a test-owned fixed-scope clone'

    & $syntheticCollectorModule {
    param([string]$testRoot, [string]$collectorSource)

    Assert-StorageTrue ($PSBoundParameters.ContainsKey('testRoot') -and -not [string]::IsNullOrWhiteSpace($testRoot)) 'private module seam must receive the synthetic root'

    foreach ($contentReadPrimitive in @('OpenRead', 'OpenText', 'ReadAllBytes', 'ReadAllLines', 'ReadAllText', 'ReadToEnd', 'Get-Content')) {
        Assert-StorageTrue (-not $collectorSource.Contains($contentReadPrimitive)) "collector must not use file-content primitive $contentReadPrimitive"
    }

    $approved = Assert-StorageExactRoot -Root $testRoot -ExpectedRoot $testRoot
    Assert-StorageEqual ([IO.Path]::GetFullPath($testRoot).TrimEnd('\')) $approved 'exact synthetic root should be accepted'

    $differentRoot = Join-Path $testRoot 'different'
    [IO.Directory]::CreateDirectory($differentRoot) | Out-Null
    Assert-StorageThrowsReason -ReasonCode 'root_not_allowlisted' -Action {
        Assert-StorageExactRoot -Root $differentRoot -ExpectedRoot $testRoot | Out-Null
    }
    Assert-StorageThrowsReason -ReasonCode 'elevated_execution_rejected' -Action {
        Assert-StorageNormalToken -IsElevatedOverride $true
    }
    Assert-StorageNormalToken -IsElevatedOverride $false

    $fixedDrive = [pscustomobject]@{ Name = 'C:\'; IsReady = $true; DriveType = 'Fixed' }
    Assert-StorageFixedReadyDrive -Drive $fixedDrive
    Assert-StorageThrowsReason -ReasonCode 'drive_not_ready' -Action {
        Assert-StorageFixedReadyDrive -Drive ([pscustomobject]@{ Name = 'C:\'; IsReady = $false; DriveType = 'Fixed' })
    }
    Assert-StorageThrowsReason -ReasonCode 'drive_not_fixed' -Action {
        Assert-StorageFixedReadyDrive -Drive ([pscustomobject]@{ Name = 'C:\'; IsReady = $true; DriveType = 'Network' })
    }

    $ordinary = Join-Path $testRoot 'ordinary.txt'
    [IO.File]::WriteAllBytes($ordinary, [byte[]](1, 2, 3, 4))
    $protected = Join-Path $testRoot '.ssh'
    [IO.Directory]::CreateDirectory($protected) | Out-Null
    [IO.File]::WriteAllBytes((Join-Path $protected 'not-enumerated.bin'), [byte[]](5, 6, 7))
    $documents = Join-Path $testRoot 'Documents'
    [IO.Directory]::CreateDirectory($documents) | Out-Null
    [IO.File]::WriteAllBytes((Join-Path $documents 'not-enumerated.bin'), [byte[]](5, 6, 7))
    $protectedFileNames = @(
        'id_rsa',
        'id_ecdsa',
        'id_ed25519',
        'id_ecdsa_sk',
        'id_ed25519_sk',
        'ID_ED25519_SK.old',
        'Id_EcDsA_sK-copy',
        'id_rsa.pub.backup',
        '.bash_history.bak',
        'certificate.pem.backup',
        'putty.PPK',
        'service.KEY~'
    )
    foreach ($protectedName in $protectedFileNames) {
        [IO.File]::WriteAllBytes((Join-Path $testRoot $protectedName), [byte[]](8, 9))
        Assert-StorageTrue (Test-StorageProtectedFileName -Name $protectedName) "protected identity or key form must match before metadata access: $protectedName"
    }
    foreach ($protectedDirectoryName in @('Google Chrome User Data', 'MOZILLA FIREFOX PROFILES', 'Microsoft Edge Profile Default', 'BraveSoftware User Data', '1PASSWORD 8', 'KeePassXC Databases')) {
        $protectedDirectory = Join-Path $testRoot $protectedDirectoryName
        [IO.Directory]::CreateDirectory($protectedDirectory) | Out-Null
        [IO.File]::WriteAllBytes((Join-Path $protectedDirectory 'vault.bin'), [byte[]](5, 6, 7))
    }

    $records = @(Invoke-StorageFixedDownloadsTraversal)
    $warningReasons = @($records | Where-Object { $_.record_type -eq 'warning' } | ForEach-Object { $_.reason_code })
    $entryPaths = @($records | Where-Object { $_.record_type -eq 'entry' } | ForEach-Object { $_.relative_path })
    Assert-StorageEqual 'scope' $records[0].record_type 'scope must be first'
    Assert-StorageEqual 'completion' $records[-1].record_type 'completion must be last'
    Assert-StorageEqual 'incomplete' $records[-1].reason_code 'protected skip must mark stream incomplete'
    Assert-StorageTrue ($warningReasons -contains 'protected_directory_skipped') 'protected directory warning is required'
    Assert-StorageTrue ($warningReasons -contains 'protected_file_skipped') 'protected file warning is required'
    Assert-StorageTrue (-not ($entryPaths -contains '.ssh/not-enumerated.bin')) 'protected contents must not be traversed'
    Assert-StorageTrue (-not ($entryPaths -contains 'Documents/not-enumerated.bin')) 'Documents contents must not be traversed'
    Assert-StorageTrue (-not ($entryPaths -contains '.ssh')) 'protected directory metadata must not be emitted'
    Assert-StorageTrue (-not ($entryPaths -contains 'Documents')) 'Documents metadata must not be emitted'
    Assert-StorageTrue (-not ($entryPaths -contains 'id_rsa')) 'protected key metadata must not be emitted'
    foreach ($protectedName in $protectedFileNames) {
        Assert-StorageTrue (-not ($entryPaths -contains $protectedName)) "protected identity or key metadata must not be emitted: $protectedName"
    }
    Assert-StorageTrue (-not ($entryPaths -contains '.bash_history.bak')) 'backup history metadata must not be emitted'
    Assert-StorageTrue (-not ($entryPaths -contains 'certificate.pem.backup')) 'backup PEM metadata must not be emitted'
    Assert-StorageTrue (-not ($entryPaths -contains 'putty.PPK')) 'PPK metadata must not be emitted case-insensitively'
    Assert-StorageTrue (-not ($entryPaths -contains 'service.KEY~')) 'backup KEY metadata must not be emitted case-insensitively'
    foreach ($protectedDirectoryName in @('Google Chrome User Data', 'MOZILLA FIREFOX PROFILES', 'Microsoft Edge Profile Default', 'BraveSoftware User Data', '1PASSWORD 8', 'KeePassXC Databases')) {
        Assert-StorageTrue (-not ($entryPaths -contains $protectedDirectoryName)) "protected directory metadata must not be emitted: $protectedDirectoryName"
        Assert-StorageTrue (-not ($entryPaths -contains ($protectedDirectoryName + '/vault.bin'))) "protected directory contents must not be emitted: $protectedDirectoryName"
    }
    Assert-StorageTrue ($entryPaths -contains 'ordinary.txt') 'ordinary metadata should be emitted'

    $fixedTraversalCommand = Get-Command 'Invoke-StorageFixedDownloadsTraversal' -CommandType Function -ErrorAction Stop
    $boundedTokens = $null
    $boundedParseErrors = $null
    $fixedTraversalAst = [Management.Automation.Language.Parser]::ParseInput(
        $fixedTraversalCommand.Definition,
        [ref]$boundedTokens,
        [ref]$boundedParseErrors
    )
    Assert-StorageEqual 0 @($boundedParseErrors).Count 'fixed traversal must parse for the test-owned source-level enumerator seam'
    $boundedAssignments = @(
        $fixedTraversalAst.FindAll(
            {
                param($node)
                $node -is [Management.Automation.Language.AssignmentStatementAst] -and
                    $node.Left.Extent.Text -eq '$getBoundedCandidates'
            },
            $true
        )
    )
    Assert-StorageEqual 1 $boundedAssignments.Count 'fixed traversal must contain one transient bounded-enumerator operation'
    $boundedEnumeratorOperation = & ([scriptblock]::Create(
        $boundedAssignments[0].Right.Extent.Text
    ))

    $partialState = @{
        InspectionCount = 0
        Exhausted = $false
    }
    $partialWarnings = [Collections.Generic.List[string]]::new()
    $partialEnumerator = [StoragePartialFailureEnumerator]::new([object[]]@('b.txt', 'a.txt'))
    $state = $partialState
    $MaximumEntries = 5
    $addWarning = {
        param([string]$ReasonCode)
        $partialWarnings.Add($ReasonCode)
    }
    $partialCandidates = @(
        & $boundedEnumeratorOperation $partialEnumerator
    )
    Assert-StorageEqual 2 $partialState.InspectionCount 'every candidate yielded before enumerator failure must consume inspection budget'
    Assert-StorageEqual 2 $partialCandidates.Count 'candidates yielded before enumerator failure must remain available for processing'
    Assert-StorageEqual 'a.txt' $partialCandidates[0] 'partial candidates must remain deterministically sorted'
    Assert-StorageEqual 'b.txt' $partialCandidates[1] 'partial candidates must remain deterministically sorted'
    Assert-StorageEqual 3 $partialEnumerator.MoveNextCalls 'partial enumerator must fail only after two yielded candidates'
    Assert-StorageTrue ($partialWarnings -contains 'enumeration_failed') 'partial enumerator failure must emit a bounded warning'

    $limitState = @{
        InspectionCount = 0
        Exhausted = $false
    }
    $limitWarnings = [Collections.Generic.List[string]]::new()
    $limitEnumerator = [StoragePartialFailureEnumerator]::new([object[]]@('c.txt', 'b.txt', 'a.txt'))
    $state = $limitState
    $MaximumEntries = 2
    $addWarning = {
        param([string]$ReasonCode)
        $limitWarnings.Add($ReasonCode)
    }
    $limitCandidates = @(
        & $boundedEnumeratorOperation $limitEnumerator
    )
    Assert-StorageEqual 2 $limitState.InspectionCount 'hard limit must charge exactly the yielded candidates'
    Assert-StorageEqual 2 $limitCandidates.Count 'hard limit must return only charged candidates'
    Assert-StorageEqual 2 $limitEnumerator.MoveNextCalls 'hard limit must not retrieve one extra candidate'
    Assert-StorageTrue ([bool]$limitState.Exhausted) 'hard limit must stop later enumeration'
    Assert-StorageTrue ($limitWarnings -contains 'max_entries_reached') 'hard limit must emit its bounded truncation warning'

    Assert-StorageEqual 'access_denied' (Get-StorageExceptionReason -Exception ([UnauthorizedAccessException]::new('raw path is not emitted'))) 'access failure must map to a bounded reason'
    Assert-StorageEqual 'enumeration_failed' (Get-StorageExceptionReason -Exception ([IO.IOException]::new('raw path is not emitted')) -Enumeration) 'enumeration failure must map to a bounded reason'
    $warningJson = (New-StorageWarningRecord -ReasonCode 'access_denied') | ConvertTo-Json -Compress
    Assert-StorageTrue (-not $warningJson.Contains('raw path')) 'warning JSON must not contain raw exception text'
    Assert-StorageTrue (-not $warningJson.Contains('relative_path')) 'warning JSON must not contain a path field'

    $junctionTarget = Join-Path $testRoot 'junction-target'
    $junctionPath = Join-Path $testRoot 'junction-entry'
    [IO.Directory]::CreateDirectory($junctionTarget) | Out-Null
    [IO.File]::WriteAllBytes((Join-Path $junctionTarget 'not-followed.txt'), [byte[]](1))
    $junctionCreated = $false
    try {
        New-Item -ItemType Junction -Path $junctionPath -Target $junctionTarget -ErrorAction Stop | Out-Null
        $junctionCreated = $true
    }
    catch {
        $global:StorageSkipped++
    }
    if ($junctionCreated) {
        $junctionRecords = @(Invoke-StorageFixedDownloadsTraversal)
        $junctionReasons = @($junctionRecords | Where-Object { $_.record_type -eq 'warning' } | ForEach-Object { $_.reason_code })
        $junctionPaths = @($junctionRecords | Where-Object { $_.record_type -eq 'entry' } | ForEach-Object { $_.relative_path })
        Assert-StorageTrue ($junctionReasons -contains 'reparse_point_skipped') 'junction must be reported as a skipped reparse point'
        Assert-StorageTrue (-not ($junctionPaths -contains 'junction-entry')) 'junction metadata must not be emitted as an ordinary directory'
        Assert-StorageTrue (-not ($junctionPaths -contains 'junction-entry/not-followed.txt')) 'junction contents must never be followed'
    }

    $sampleRecords = @(
        (New-StorageCapacityScopeRecord -TotalBytes 1000 -FreeBytes 250),
        (New-StorageTraversalScopeRecord),
        (New-StorageEntryRecord -RelativePath 'synthetic/file.txt' -EntryType 'file' -SizeBytes 12 -ModifiedUtc ([datetime]'2026-08-08T12:00:00Z')),
        (New-StorageCompletionRecord -ReasonCode 'complete')
    )
    $jsonLines = @($sampleRecords | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 3 })
    Assert-StorageEqual 4 $jsonLines.Count 'JSONL sample must contain one object per line'
    $parsed = @($jsonLines | ForEach-Object { $_ | ConvertFrom-Json })
    Assert-StorageEqual 1 $parsed[0].schema_version 'schema version must be compatible'
    Assert-StorageEqual 'windows' $parsed[2].collector 'collector name must be compatible'
    Assert-StorageEqual 'synthetic/file.txt' $parsed[2].relative_path 'relative path must use shared separators'
    Assert-StorageTrue ([string]$parsed[2].modified_utc -match '\.\d{7}Z$') 'Windows timestamps must preserve their seven-digit tick precision'
    $expectedKeys = @('schema_version', 'record_type', 'collector', 'root_alias', 'root_kind', 'relative_path', 'entry_type', 'size_bytes', 'modified_utc')
    $actualKeys = @($parsed[2].PSObject.Properties.Name)
    Assert-StorageEqual 0 (@(Compare-Object $expectedKeys $actualKeys).Count) 'entry JSON fields must be exact'

    } $testRoot $collectorSource

    [Console]::Out.WriteLine("PASS: $global:StorageAssertions assertions; $global:StorageSkipped environment-dependent checks skipped")
}
finally {
    if ([IO.Directory]::Exists($testRoot)) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
