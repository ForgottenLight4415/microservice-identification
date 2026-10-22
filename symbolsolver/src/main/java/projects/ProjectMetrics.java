package projects;

public class ProjectMetrics {

    private Project project;
    private double irn;
    private double opn;

    public ProjectMetrics(Project project) {
        this.project = project;
    }

    public Project getProject() {
        return project;
    }

    public double getIrn() {
        return irn;
    }

    public void setIrn(double irn) {
        this.irn = irn;
    }

    public double getOpn() {
        return opn;
    }

    public void setOpn(double opn) {
        this.opn = opn;
    }

    @Override
    public String toString() {
        return "ProjectMetrics{" +
                "project=" + project.getName()+
                ", irn=" + irn +
                ", opn=" + opn +
                '}';
    }
}
