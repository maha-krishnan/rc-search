@Library('rightrev-lib') _

pipeline {
    agent any
    environment {
        IMAGE_NAME = "rc-search"
    }
    stages {
        stage('build') {
            steps {
                print "${env.JOB_NAME}: ${env.STAGE_NAME}"
                sh 'printenv'
                cleanWs()
                checkout scm
                dir('src') {
                    sh "docker system prune -f"
                    buildDocker()
                }
                notifySlack("#build", "${env.JOB_NAME}: ${env.STAGE_NAME} completed", "green")
            }
        }
        stage('test') {
            steps {
                print "${env.JOB_NAME}: ${env.STAGE_NAME}"
                dir('src') {
                    sh "make docker-test || true"
                    testReport('reports')
                }
            }
        }
        stage('bake') {
            steps {
                print "${env.JOB_NAME}: ${env.STAGE_NAME}"
                dir('src') {
                    pushToECR()
                }
            }
        }
        stage('deploy') {
            steps {
                print "${env.JOB_NAME}: ${env.STAGE_NAME}"
                dir('deployment') {
                    deployInK8S()
                }
            }
        }
    }

    post {
        success {
            postSlack("success")
        }
        failure {
            postSlack("failure")
        }
    }
}
