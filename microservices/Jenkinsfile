pipeline {
    agent any

    environment {
        SONAR_CLOUD_URL = 'https://sonarcloud.io'
        SONAR_PROJECT_KEY = 'devops-group15_lab2'
        appRegistry = 'phihung1607' 
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: 'gitsshkeys', url: 'https://github.com/hhunng/lab2-devops.git'
            }
        }

        stage('SonarCloud Scan') {
            steps {
                script {
                    scannerHome = tool 'sonarQube'
                }
                withSonarQubeEnv('sonarQube') {
                    sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=${SONAR_CLOUD_URL}
                    """
                }
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build App Images') {
            steps {
                script {
                    def appServices = [
                        ["service": "billing-service", "dir": "./billing-service/"],
                        ["service": "user-svc", "dir": "./user-service/"],
                        ["service": "subscription-svc", "dir": "./subscription-service/"],
                        ["service": "db_postgres", "dir": "./db-service/"]
                    ]
                    appServices.each { app ->
                        def imageName = "${appRegistry}/${app.service}:${BUILD_NUMBER}"
                        echo "Building Docker image for service: ${app.service} from directory: ${app.dir}"
                        dockerImage = docker.build(imageName, app.dir)
                    }
                } 
            }
        }

        stage('Push Images to Docker Hub') {
            steps {
                script {
                    def appServices = [
                        ["service": "billing-service"],
                        ["service": "user-svc"],
                        ["service": "subscription-svc"],
                        ["service": "db_postgres"]
                    ]

                    appServices.each { app ->
                        def imageName = "${appRegistry}/${app.service}:${BUILD_NUMBER}"
                        echo "Pushing Docker image: ${imageName} to Docker Hub"
                        docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                            docker.image(imageName).push("$BUILD_NUMBER")
                            docker.image(imageName).push('latest')
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'SonarCloud scan completed.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for more details.'
        }
    }
}