import jenkins.model.Jenkins

System.setProperty('org.jenkinsci.pipeline.stageview.disabledOnMainJobPage', 'true')

def applyBooleanSetting = { Object target, String setterName, boolean value ->
    def method = target.class.methods.find {
        it.name == setterName &&
            it.parameterTypes.length == 1 &&
            (it.parameterTypes[0] == Boolean.TYPE || it.parameterTypes[0] == Boolean.class)
    }

    if (method == null) {
        println "[cloudnotes-pipeline-ui] ${setterName} is not available in this plugin version."
        return false
    }

    method.invoke(target, value)
    println "[cloudnotes-pipeline-ui] ${setterName}=${value}"
    return true
}

try {
    def loader = Jenkins.get().pluginManager.uberClassLoader
    def configClass = loader.loadClass('io.jenkins.plugins.pipelinegraphview.PipelineGraphViewConfiguration')
    def graphConfig = configClass.getMethod('get').invoke(null)

    applyBooleanSetting(graphConfig, 'setShowGraphOnJobPage', true)
    applyBooleanSetting(graphConfig, 'setShowStageNames', true)
    applyBooleanSetting(graphConfig, 'setShowStageDurations', true)
    applyBooleanSetting(graphConfig, 'setShowGraphOnBuildPage', true)

    graphConfig.save()
    Jenkins.get().save()
    println '[cloudnotes-pipeline-ui] Pipeline visualization defaults configured.'
} catch (ClassNotFoundException ignored) {
    println '[cloudnotes-pipeline-ui] Pipeline Graph View plugin is not installed; skipped.'
} catch (Throwable t) {
    println "[cloudnotes-pipeline-ui] Pipeline visualization defaults failed: ${t.class.simpleName}: ${t.message}"
}
