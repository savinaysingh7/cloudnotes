import jenkins.model.Jenkins
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.SystemCredentialsProvider
import com.cloudbees.plugins.credentials.domains.Domain
import com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl
import com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey

String stripBom(String value) {
    return value == null ? null : value.replaceFirst('^\uFEFF', '')
}

String readSecret(String envName, List<String> filePaths, boolean trimValue) {
    String envValue = System.getenv(envName)
    if (envValue != null && stripBom(envValue).trim()) {
        return trimValue ? stripBom(envValue).trim() : stripBom(envValue)
    }

    for (String path : filePaths) {
        File secretFile = new File(path)
        if (secretFile.exists() && secretFile.isFile()) {
            String fileValue = stripBom(secretFile.getText('UTF-8'))
            if (fileValue != null && fileValue.trim()) {
                return trimValue ? fileValue.trim() : fileValue
            }
        }
    }

    return null
}

String normalizePrivateKey(String privateKey) {
    return stripBom(privateKey).replace('\r\n', '\n').replace('\r', '\n').trim() + '\n'
}

def jenkins = Jenkins.get()
def provider = jenkins.getExtensionList(SystemCredentialsProvider.class)[0]
def store = provider.getStore()
def domain = Domain.global()

String dockerHubUser = System.getenv('CLOUDNOTES_DOCKERHUB_USERNAME')?.trim() ?: 'savinaysingh7'
String dockerHubPassword = readSecret(
    'CLOUDNOTES_DOCKERHUB_PASSWORD',
    ['/var/jenkins_home/cloudnotes-secrets/dockerhub_password'],
    true
)
String appSshPrivateKey = readSecret(
    'CLOUDNOTES_APP_SSH_PRIVATE_KEY',
    ['/var/jenkins_home/cloudnotes-secrets/app_ssh_private_key'],
    false
)

if (!dockerHubPassword || !appSshPrivateKey) {
    println '[cloudnotes-creds] Secret files are not present yet; credential injection skipped.'
} else {
    def upsertCredential = { credential ->
        def existing = store.getCredentials(domain).find { it.id == credential.id }
        if (existing) {
            store.updateCredentials(domain, existing, credential)
        } else {
            store.addCredentials(domain, credential)
        }
    }

    upsertCredential(new UsernamePasswordCredentialsImpl(
        CredentialsScope.GLOBAL,
        'dockerhub-credentials',
        'Docker Hub credentials for CloudNotes image pushes',
        dockerHubUser,
        dockerHubPassword
    ))

    upsertCredential(new BasicSSHUserPrivateKey(
        CredentialsScope.GLOBAL,
        'app-server-ssh-key',
        'ubuntu',
        new BasicSSHUserPrivateKey.DirectEntryPrivateKeySource(normalizePrivateKey(appSshPrivateKey)),
        '',
        'CloudNotes app server SSH key'
    ))

    provider.save()
    jenkins.save()
    println '[cloudnotes-creds] Credentials installed: dockerhub-credentials, app-server-ssh-key'
}
