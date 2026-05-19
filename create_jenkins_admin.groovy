import jenkins.model.*
import hudson.security.*

println('-- creating ciadmin user --')
def instance = Jenkins.getInstance()
def realm = instance.getSecurityRealm()
if (realm instanceof HudsonPrivateSecurityRealm) {
  def user = realm.getUser("ciadmin")
  if (user == null) {
    realm.createAccount("ciadmin","ChangeMe!2026")
    println('ciadmin created')
  } else {
    println('ciadmin already exists')
  }
  instance.save()
} else {
  println('security realm is not HudsonPrivateSecurityRealm; skipping')
}
