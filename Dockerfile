FROM continuumio/miniconda3

# Set up the environment
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

# Copy the environment.yml to the container
COPY environment.yml /app/environment.yml

# Create the conda environment
RUN conda env create -f /app/environment.yml

# Set the working directory
WORKDIR /app

# Copy the rest of the application code to the container
COPY . /app

# Activate the conda environment and ensure it's activated
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Install Gradio (if not included in environment.yml)
RUN pip install gradio

# Expose the port Gradio will run on
EXPOSE 7860

# Command to run the Gradio app
CMD ["conda", "run", "--no-capture-output", "-n", "myenv", "python", "gradio_gui.py"]
