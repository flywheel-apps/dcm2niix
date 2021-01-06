# Development tag
TAG=1.2.1_1.0.20201102_dev2
LOCAL='no'

# Make upload directory
UPLOAD_DIR=${HOME}/gears/upload_zone
mkdir -p ${UPLOAD_DIR}

# Copy necessary files to upload directory
cp Dockerfile ${UPLOAD_DIR}
cp manifest.json ${UPLOAD_DIR}
cp requirements.txt ${UPLOAD_DIR}
cp run.py ${UPLOAD_DIR}
cp -r dcm2niix/ ${UPLOAD_DIR}
cp -r pydeface/ ${UPLOAD_DIR}
cp -r utils/ ${UPLOAD_DIR}

cd ${UPLOAD_DIR}
echo ${PWD}

# Build the docker image
docker build -t flywheel/dcm2niix:${TAG} ./

# Test gear locally
if [ ${LOCAL} == 'yes' ]; then
	fw gear local --dcm2niix_input ~/gears/dcm2niix/tests/assets/aliza_siemens_trio.zip
fi

# Finish 
echo "Finished."
