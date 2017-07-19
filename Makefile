ACBDIR = acb
ACIDIR = aci

.PHONY: all clean

all: $(ACIDIR)/kafka.aci $(ACIDIR)/zookeeper.aci

$(ACIDIR)/%.aci: $(ACBDIR)/build-%.acb
	@mkdir -p $(ACIDIR)
	@cd $(ACIDIR) && acbuild-script ../$<

clean:
	rm -rf $(ACIDIR)
