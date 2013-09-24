dirListing = dir('.');
imgListing = dir('./img');

for d = 1:length(dirListing)
    if ~dirListing(d).isdir && ~isempty(strfind(dirListing(d).name, '.txt')) && ~isempty(strfind(dirListing(d).name, 'Pe_'))

        efilename = dirListing(d).name;
        ifilename = strrep(efilename,'Pe_','Pi_');
        flist=struct2cell(dirListing);
        ilist=struct2cell(imgListing);

        if ~ismember(strrep(efilename,'.txt','.png'),ilist(1,:))
            Me = load(efilename);
            Mi = load(ifilename);

            if sum(size(Me)) >0 && sum(size(Mi)) >0
                f = figure;
                set(f,'visible','off')

                subplot(2,1,1)
                scatter(Me(:,2),Me(:,1),10,'k','fill','s');
                title(strrep(efilename,'.txt',''));
                axis([0,max(Mi(:,2)),0,100]);

                subplot(2,1,2)
                scatter(Mi(:,2),Mi(:,1),10,'k','fill','s');
                title(strrep(ifilename,'.txt',''));
                axis([0,max(Mi(:,2)),0,100]);

                saveas(f,['img/',strrep(efilename,'.txt','.png')]);
            end
        end
    end
end
