# lemniscat.plugin.azurecli
A plugin to operate Azure services through Azure cli into a lemniscat workflow

## Description
This plugin allows you to operate Azure services through Azure cli into a lemniscat manifest.

## Usage
### Pre-requisites
In order to use this plugin, you need to have an Azure subscription and an Azure service principal. You can create a service principal using the Azure CLI, PowerShell, or the Azure portal. The service principal is used to authenticate the Azure CLI to your Azure subscription.

After that you to be sure that you have the Azure CLI installed on your agent. You can install it using the following command:

#### Linux
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

#### Windows
```powershell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
```

You need also set environment variables to authenticate the Azure CLI to your Azure subscription.
- `ARM_SUBSCRIPTION_ID` : The subscription ID that you want to use
- `ARM_CLIENT_ID` : The client ID of the service principal
- `ARM_CLIENT_SECRET` : The client secret of the service principal
- `ARM_TENANT_ID` : The tenant ID of the service principal

You need to add plugin into the required section of your manifest file.
```yaml
requirements:
  - name: lemniscat.plugin.azurecli
    version: 0.1.0.9
```

### Running powershell commands with Azure CLI
```yaml
- task: azurecli
  displayName: 'Azure CLI'
  steps:
    - run
  parameters:
    scripttype: pwsh
    commandtype: inline
    script: |
      $version = az --version
      Write-Host "Azure CLI version: $version"
```

### Running powershell script with Azure CLI
```yaml
- task: azurecli
  displayName: 'Azure CLI'
  steps:
    - run
  parameters:
    scripttype: pwsh
    commandtype: file
    filePath: ${{ workingdirectory }}/scripts/ClearAzureContainer.ps1
    fileParams:
      storageAccountName: ${{ storageAccountName }}
      containerName: ${{ containerName }}
```
### Running powershell commmands and pass variables through json file
> [!NOTE] 
> This feature is particulary recommand when you need to manipulate complexe variable with your task.
> You can access to the variables in the json file by using the following command:
> ```powershell
> $location = Get-Location
> $variables = Get-Content "$($location.path)/vars.json" | ConvertFrom-Json -Depth 100
> ```

```yaml
- task: azurecli
  displayName: 'Azure CLI'
  steps:
    - run
  parameters:
    scripttype: pwsh
    commandtype: inline
    script: |
      $location = Get-Location
      $variables = Get-Content "$($location.path)/vars.json" | ConvertFrom-Json -Depth 100
      $version = az --version
      Write-Host "Azure CLI version: $version"
    storeVariablesInFile:
      format: json
      withSecrets: false
```

## Inputs

### Parameters
- `scripttype`: The type of the script to run. It can be only `pwsh` (for the moment)
- `commandtype`: The type of the command to run. It can be `inline` or `file`
- `script`: The script to run. It can be a powershell command line. It is used only if `commandtype` is `inline`
- `filePath`: The path of the powershell script file (*.ps1) to run. It is used only if `commandtype` is `file`
- `fileParams`: The parameters to pass to the powershell script file. It is used only if `commandtype` is `file`
- [`storeVariablesInFile`](#StoreVariablesInFile): Describe the way to store the variables in a file to used in the task.

#### StoreVariablesInFile
- `format`: The format of the file to store the variables. It can be `json` or `yaml`
- `withSecrets`: A boolean value to indicate if the secrets should be stored in the file. It can be `true` or `false`

## Outputs

You can push variables to the lemniscat runtime in order to be used after by other tasks.
To do that, you need to use `Write-Host` command in your powershell script to push variables to the lemniscat runtime.
You must use the following format to push variables to the lemniscat runtime:
`[lemniscat.pushvar] <variableName>=<variableValue>`

For example:
```powershell
Write-Host "[lemniscat.pushvar] workspaceExist=$workspaceExist"
```

You can specify the sensitivity of the variable by adding `secret` like this :
`[lemniscat.pushvar.secret] <variableName>=<variableValue>`

For example:
```powershell
Write-Host "[lemniscat.pushvar.secret] storageAccountKey=$storageAccountKey"
```